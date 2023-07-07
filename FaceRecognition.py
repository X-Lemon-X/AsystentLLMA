import face_recognition
import os
import cv2
import numpy as np
import math
import copy
from pathlib import Path
from threading import Thread, Event , Lock
import time as timer

MAX_FACE_ID = 99999999999
MIN_FACE_ID = 10000000000

VERIFIED_FACE_DIR_NAME = "verified"
UNVERIFIED_FACE_DIR_NAME = "unverified"
FACES_DIR_NAME = "faces"
TEST_CAPTURE = False
RESIZE_FACE_BOX_CONSTANT = 0.1  #resize by 10% to avoid cutting face


class FacesLib:
  def __init__(self, video_frame_resize = 0.25, camera=cv2.VideoCapture(0),faces_path:str = FACES_DIR_NAME) -> None:
    if faces_path is None or faces_path == "":
      raise ValueError("faces_path must be not empty")
    Path.mkdir(Path(faces_path),exist_ok=True)
    Path.mkdir(Path(faces_path +'/'+ VERIFIED_FACE_DIR_NAME),exist_ok=True)
    Path.mkdir(Path(faces_path+'/'+UNVERIFIED_FACE_DIR_NAME),exist_ok=True)

    self.video_frame_resize = video_frame_resize


    self.face_locations = [] #holde curent frame face locations for acelerated face recognition
    self.face_encodings = [] #holde curent frame face encodings for acelerated face recognition
    self.face_names = [] #holde curent frame face names for acelerated face recognition
    self.face_confidences = [] #holde curent frame face confidences for acelerated face recognition
    self.face_to_image_ratio = [] #holde curent frame face to image ratio in percentage 0-1  where 1 is 100% face filling a image

    # for pulling data out of threads and higher performance
    self.curent_names =[] 
    self.curent_confidences = []
    self.curent_face_to_image_ratio = []

    #holde face id's for filering
    self.filer_faces_ids = {}
    self.filter_delta_time = 1.0 #time in seconds to filter faces that are not in the frame but where in previous frames to avoid flickering of the output of curently available faces
    self.fec = {}
    self.fec_copy = {}


    self.known_face_encodings = []
    self.known_face_names = []
    self.known_face_images = []
    self.verified_face = []
    self.faces_path = faces_path +'/'+ VERIFIED_FACE_DIR_NAME
    self.faces_path_unverified = faces_path+'/'+UNVERIFIED_FACE_DIR_NAME
    self.videoCapture = camera

    self.CameraThreadEvent = Event()
    self.CameraThreadEvent.clear()
    self.CameraThreadLock = Lock()
    self.CameraThread = Thread(target=self.__CaptureThread)
  
  def __del__(self):
    self.__StopThread()
    self.videoCapture.release()
    self.SaveFaces()

  def __str__(self) -> str:
    return str(list(zip(self.known_face_names,self.verified_face))) 

  def LoadFromPath(self,faces_path:str, areVerified:bool = True,removeImagesWithoutFace:bool = True):
    for image in os.listdir(faces_path):
      image_path = os.path.join(faces_path, image)
      try:
        img2 = cv2.imread(image_path)
        rgb_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        face_encoding = face_recognition.face_encodings(rgb_img2)[0]
        id = int(os.path.basename(os.path.splitext(image)[0]))
        
        self.known_face_images.append(rgb_img2)
        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(id)
        self.verified_face.append(areVerified)
      except:
        print("Error in Loading", image_path)
        if removeImagesWithoutFace:
          os.remove(image_path)

  def LoadFaces(self, removeImagesWithoutFace = True):
    self.LoadFromPath(self.faces_path_unverified,False,removeImagesWithoutFace)
    self.LoadFromPath(self.faces_path,True,removeImagesWithoutFace)

  def AddFaceFromPath(self,stringPath:str, verified:bool = False):
    img2 = cv2.imread(stringPath)
    rgb_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    face_encoding = face_recognition.face_encodings(rgb_img2)[0]
    self.known_face_encodings.append(face_encoding)
    self.known_face_names.append(os.path.basename(stringPath))
    self.known_face_images.append(rgb_img2)
    self.verified_face.append(verified)

  def AddFace(self,face_encoding:list,image_with_face, face_location:list =None, verified = False) -> int:
    id = np.random.randint(MIN_FACE_ID,MAX_FACE_ID)
    while id in self.known_face_names:  
      id = np.random.randint(MIN_FACE_ID,MAX_FACE_ID)

    if face_location is not None:
      top, right, bottom, left = face_location
      top = int(top - top*RESIZE_FACE_BOX_CONSTANT)
      right = int(right + right*RESIZE_FACE_BOX_CONSTANT)
      bottom = int(bottom + bottom*RESIZE_FACE_BOX_CONSTANT)
      left = int(left - left*RESIZE_FACE_BOX_CONSTANT)

      image = image_with_face[top:bottom]
      image = image[:,left:right]
      image_with_face = image

    self.known_face_names.append(id)
    self.known_face_encodings.append(face_encoding)
    self.known_face_images.append(image_with_face)
    self.verified_face.append(verified)
    return id , len(self.known_face_names)-1

  def VerifyFace(self,face_id:int):
    try: 
      index = self.known_face_names.index(face_id)
      self.verified_face[index] = True
    except:
      raise ValueError("Face id not found")

  def SaveFaces(self):
    for i in range(len(self.known_face_encodings)):
      image = self.known_face_images[i]
      face_name = self.known_face_names[i]
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      path = ""
      if self.verified_face[i]:
        path = os.path.join(self.faces_path,str(face_name)+".jpg")
      else:
        path = os.path.join(self.faces_path_unverified,str(face_name)+".jpg")
      cv2.imwrite(path,image)

  def RemoveFace(self,face_id:int):
    index = self.known_face_names.index(face_id)
    self.known_face_names.pop(index)
    self.known_face_encodings.pop(index)
    self.known_face_images.pop(index)
    self.verified_face.pop(index)

  def __FilterFaces(self, faces_names:list = None, faces_confidences:list = None, faces_to_image_ratio:list = None, fec:dict = None):
    """Filetr faces that are not in the frame but where in previous frames to avoid flickering of the output of curently available faces"""
    if faces_names is None:
      pass
      
    if fec is None:
      fec = {}

    keysToRemove = []
    curentTime = timer.time()
    for key, time in self.filer_faces_ids.items():
      if curentTime - time > self.filter_delta_time:
        keysToRemove.append(key)
    
    for key in keysToRemove:
      self.filer_faces_ids.pop(key)
      self.fec.pop(key)

    if len(fec) != 0:
      curentTime = timer.time()
      for key, value in fec.items():
        self.filer_faces_ids[key] = curentTime
        self.fec[key] = fec[key]

    # for higher performance on multithreading rather than stoping entire capture proces to get data
    # just copy results to another variables that are locked 
    with self.CameraThreadLock:
      self.fec_copy = copy.deepcopy(self.fec)

  def __CompareFaces(self,face_encoding:list):
    """ return True if face is recognized
        return False if face is not recognized is not on a list """
    if len(self.known_face_encodings) == 0:
      return None, None
    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
      return best_match_index , face_distances[best_match_index]
    else :
      return None , None

  def __RunCapture(self):
    """ runs single capthure frame from camera and perform face recognition """
    ret, frame = self.videoCapture.read()
    if not ret:
      print("Error reading frame from camera")
      return False
    frameCopy = copy.deepcopy(frame)
    
    if self.video_frame_resize != 1.0:
      small_frame = cv2.resize(frame, (0, 0), fx=self.video_frame_resize, fy=self.video_frame_resize)
    else:
      small_frame = frame

    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    self.face_locations = face_recognition.face_locations(rgb_small_frame)
    self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

    faces_in_a_frame = {}    
    if TEST_CAPTURE:
      self.face_names = []
      self.face_to_image_ratio = []
      self.face_confidences = []
      verified = []
    
    index = 0
    for face_encoding in self.face_encodings:
      matcheIndex, distance = self.__CompareFaces(face_encoding)
      if matcheIndex is None:
        frameCopy = cv2.cvtColor(frameCopy, cv2.COLOR_BGR2RGB)
        id , matcheIndex = self.AddFace(face_encoding,frameCopy,self.face_locations[index])
        matcheIndex, distance = self.__CompareFaces(face_encoding)
        #print("New face detected:",id)
      top, right, bottom, left = self.face_locations[index]
      face_to_image_ratio = (bottom-top)*(right-left)/(rgb_small_frame.shape[0]*rgb_small_frame.shape[1])
      
      key = self.known_face_names[matcheIndex]
      faces_in_a_frame[key] = [self.__face_confidence(distance),face_to_image_ratio,self.verified_face[matcheIndex]]
      
      if TEST_CAPTURE:
        self.face_to_image_ratio.append(face_to_image_ratio)
        self.face_confidences.append(self.__face_confidence(distance))
        self.face_names.append(self.known_face_names[matcheIndex])
        verified.append(self.verified_face[matcheIndex])
      index = index+1


    
    self.__FilterFaces(self.face_names,self.face_confidences,self.face_to_image_ratio,faces_in_a_frame)
      
    if TEST_CAPTURE:
      # Display the results
      for (top, right, bottom, left), name, ver, conf in zip(self.face_locations, self.face_names,verified, self.face_confidences):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        ratio = 1.0/self.video_frame_resize
        top = int(top* ratio)
        right = int(right*ratio)
        bottom =int(bottom* ratio)
        left =int(left* ratio)
        # Create the frame with the name
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        prefix = 'V:'
        if not ver:
          prefix = 'U:'
        cv2.putText(frame, prefix + str(int(conf)) + ">"+ str(name) , (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        # Display the resulting image
      cv2.imshow('Face Recognition', frame)
      if cv2.waitKey(1) == ord('q'):
        return False
    
    return True

  def __face_confidence(self,distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - distance) / (range * 2.0)

    if distance > face_match_threshold:
      return round(linear_val * 100, 2)
    else:
      value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
      return round(value, 2)

  def __CaptureThread(self):
    while True:
      self.__RunCapture()
      if self.CameraThreadEvent.is_set():
        break

  def __StartThread(self):
    if self.CameraThread.is_alive() is False:
      self.CameraThreadEvent.clear()
      self.CameraThread.start()
    else:
      self.CameraThreadEvent.set()
      self.CameraThread.join()
      self.CameraThreadEvent.clear()
      self.CameraThread = Thread(target=self.__CaptureThread, args=self)
      self.CameraThread.start()

  def __StopThread(self):
    if self.CameraThread.is_alive() is False:
      return
    self.CameraThreadEvent.set()
    self.CameraThread.join()
    self.CameraThreadEvent.clear()
  
  def TestCapture(self):
    """ Returns True if capture is working"""
    return self.__RunCapture()

  def StartCapture(self):
    self.__StartThread()

  def StopCapture(self):
    self.__StopThread()

  def GetCurentFaces(self):
    """ Returns list of tuples (name_face_id, confidence, face_to_image_ratio)"""
    with self.CameraThreadLock:
      return self.fec_copy
      #return [*zip(self.curent_names  , self.curent_confidences , self.curent_face_to_image_ratio)]
    
  def SetFilterDeltaTime(self, time:float):
    with self.CameraThreadLock:
      self.filter_delta_time = time

