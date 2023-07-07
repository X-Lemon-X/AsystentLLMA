from FaceRecognition import FacesLib
import json
import os


class FaceCodesWraper:
  def __init__(self,faceRecogninito:FacesLib, commands_file:str = "face_llm_wraper.json") -> None:
    self.faceRecogninito = faceRecogninito
    self.commands_file = commands_file
    if os.path.isfile(commands_file):
      self.commands = json.loads(open(commands_file).read())
    else :
      self.commands = {}
    self.functions = { "G20":self.G20, "G21":self.G21 }
  def __del__(self):
    self.faceRecogninito.StopCapture()

  def HandleCommand(self, key:str, args:str = None) -> str:
    if key in self.functions:
      return self.functions[key](args)
    raise Exception("command not found")

  def GetCommand(self) -> str:
    return self.commands

  def G20(self, args) -> str:
    faces = self.faceRecogninito.GetCurentFaces()
    if len(faces) == 0:
      return ""
    
    text = ""
    for name, ratio in faces.items():
      text += str(name) + ", "
    
    text = text[:-2]
    return text
  
  def G21(self,args) -> str:
    text = ""
    for arg in args:
      try:
        self.faceRecogninito.VerifyFace(int(arg))
      except BaseException as e:
        text += "error: " + str(e) + "\n"
    return text
  
