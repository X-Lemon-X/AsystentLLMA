import lib.FaceRecognition as FaceRecognition
from time import sleep
import cv2

faceR = FaceRecognition.FacesLib(faces_path='faces',video_frame_resize=1)

faceR.LoadFaces(False)
#faceR.StartCapture()

while True:
  try:
    if faceR.TestCapture() is False:
      break
  except KeyboardInterrupt:
    break
  except BaseException as e:
    print ("Error",e)

print(faceR)
faceR.SaveFaces()
#faceR.StopCapture()