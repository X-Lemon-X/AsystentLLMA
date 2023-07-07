from gpt4all import GPT4All
import speech_recognition as sr
import pyttsx3
import whisper
import soundfile as sf
import numpy as np
import io
from gtts import gTTS
import os
import pyaudio
import json
import FaceRecognition as fr
import FaceLibLLMWraper as flw

USE_GOOGLE_VOICE = False
USE_PYTTSX_VOICE = True

commands = json.loads(open("comands.json").read())

face = fr.FacesLib()
faceWraper = flw.FaceCodesWraper(faceRecogninito=face)
face.LoadFaces()
face.StartCapture()


modelsAudioIn = whisper.load_model("small") # base.en or small.en

microReader = sr.Recognizer()
microphone = pyaudio.PyAudio()
index = microphone.get_device_count() - 1
engineTextToSpeach = pyttsx3.init()
engineTextToSpeach.setProperty('voice', 'english')

modelSystem_Prompt = "### System:\nYou are an assistant that answear questions and can run this commands:\n"
modelInstruction_Prompt = "### Instruction:\n%1\n"
modelResponse_Prompt = "### Response:\n\n"

modelLLM = GPT4All("nous-hermes-13b.ggmlv3.q4_0.bin",n_threads=6) 
basicBotPromptSetings = "" #"Be precise, give short answears, look for cammond words line minus, plus, equal, etc. translate them as you would do in math."

ExitApp = False
Language = {"en":"english", "pl":"polish"}


PreviousCommand = None
comandResponse = None


def CreatePrompt(question:str):
  prompt = modelSystem_Prompt
  for key in commands.items():
    prompt += "comamnd " + key[0] + " does " + key[1]["des"] + ". arguments: " + key[1]["argument"] + "\n"
  prompt += "if the quesion is best explained by one of the comamnd return the name of the this command with an arguemnt if it fits the user request \n if the command can't answeat questio, answear to the question by yourself\n"

  global PreviousCommand
  global comandResponse

  if PreviousCommand is not None:
    prompt += "Previous command: " + str(PreviousCommand) + "\n"
    PreviousCommand = None
  if comandResponse is not None:
    prompt += "Previous command response: " + str(comandResponse) + "\n"
    comandResponse = None
  
  prompt += modelInstruction_Prompt 
  prompt +=basicBotPromptSetings
  prompt += question + "\n"
  return prompt

def HandleCommand(command:str):
  global PreviousCommand
  global comandResponse
  global ExitApp
  commandRun = False
  if command is None or command == "":
    return
  command = command.lower()
  for key in commands.keys():
    if command.find(key.lower()) != -1:
      commandRun = True
      PreviousCommand = key
      if key == "G1":
        comandResponse = "Patryk, Kmail, Brzezin,"
        pass
      elif key == "G2":
        ExitApp = True
        comandResponse = "exit"
      elif key == "G3":
        os.system("code")
  return commandRun

def speak(text_to_speak, language="english"): 
  if text_to_speak is None or text_to_speak == "":
    return
  if USE_GOOGLE_VOICE:
    audio = gTTS(text=text_to_speak,tld="pl", lang='en', slow=False)
    audio.save("audio.mp3")
    os.system("mpg321 audio.mp3")
  elif USE_PYTTSX_VOICE:
    engineTextToSpeach.setProperty('voice', language)
    engineTextToSpeach.say(text_to_speak)
    engineTextToSpeach.runAndWait()

def translateAudio(audio):
  if type(audio) is not sr.AudioData:
    raise TypeError("audio must be AudioData")
  wav_bytes = audio.get_wav_data(convert_rate=16000)
  wav_stream = io.BytesIO(wav_bytes)
  audio_array, sampling_rate = sf.read(wav_stream)
  audio_array = audio_array.astype(np.float32)
  resposne = modelsAudioIn.transcribe(audio=audio_array)
  text = resposne['text']
  language = resposne['language']
  print("You said:",text ,"[Language]:",language)
  return text, language

def listeToAudio(source2:sr.Microphone):
  print("Listening...")
  microReader.adjust_for_ambient_noise(source2, duration=0.2)
  return microReader.listen(source2)

def LookForBasicComands(speach:str):
  if speach is None or speach == "":
    return False
  command = speach.lower()
  if command.find("exit") != -1:
    print("Exiting...")
    global ExitApp
    ExitApp = True
    return True
  return False

def GetResponseFormLLM(llma:GPT4All,text:str):
  if text is None or text == "":
    return None
  Tos = CreatePrompt(text)
  print("Prompt: ",Tos)
  answear = llma.generate(prompt=Tos,max_tokens=4096,temp=0.8,top_p=0.9,top_k=40,n_batch=512)
  print("answear: ",answear)
  if HandleCommand(answear):
    return comandResponse
  return answear

while ExitApp is False:   
  try:
    with sr.Microphone(device_index=index) as source2, modelLLM.chat_session() as session: 
      audio = listeToAudio(source2)
      speach, lang = translateAudio(audio)
      #speach = input("You: ")
      #lang = "en"
      #if LookForBasicComands(speach) is False :
      llmResponse = GetResponseFormLLM(llma=session,text=speach)
      print("Asistant: ",llmResponse)
      if lang not in Language:
        lang = "en"
      speak(text_to_speak=llmResponse, language=Language[lang])

  except sr.RequestError as e:
      print("Could not request results; {0}".format(e))
  except sr.UnknownValueError:
      print("unknown error occurred")
  except KeyboardInterrupt as e:
      break
  except BaseException as e:
      print("unknown error occurred", {e})
