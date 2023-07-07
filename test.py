import lib.FaceRecognition as FaceRecognition
from time import sleep


faceR = FaceRecognition.FacesLib(video_frame_resize=1)

faceR.LoadFaces(False)
#faceR.StartCapture()

while True:
  try:
    if faceR.TestCapture() is False:
      break
    tab = faceR.GetCurentFaces()
    print(tab)
  except KeyboardInterrupt:
    break
  except BaseException as e:
    print ("Error",e)

print(faceR)
faceR.SaveFaces()
#faceR.StopCapture()