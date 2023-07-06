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

USE_GOOGLE_VOICE = False
USE_PYTTSX_VOICE = True

# sudo apt install espeak
#linu sudo apt-get install python3-pyaudio
#pip install SpeechRecognition
#pip install pyttsx3
#pip install gpt4all
#pip install -U openai-whisper
#sudo apt update && sudo apt install ffmpeg


#sudo apt-get install libespeak-ng1
#pip install mycroft-mimic3-tts
#pip install onnxruntime-gpu

modelsAudioIn = whisper.load_model("small") # base.en or small.en

microReader = sr.Recognizer()
microphone = pyaudio.PyAudio()
index = microphone.get_device_count() - 1
engineTextToSpeach = pyttsx3.init()
engineTextToSpeach.setProperty('voice', 'english')

modelLLM = GPT4All("nous-hermes-13b.ggmlv3.q4_0.bin",n_threads=6) 
basicBotPromptSetings = "" #"Be precise, give short answears, look for cammond words line minus, plus, equal, etc. translate them as you would do in math."

ExitApp = False
Language = {"en":"english", "pl":"polish"}

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
  return llma.generate(prompt=text,max_tokens=4096,temp=0.8,top_p=0.9,top_k=40,n_batch=512)

def mainLoop():
  with sr.Microphone(device_index=index) as source2, modelLLM.chat_session() as session:   
    audio = listeToAudio(source2)
    speach, lang = translateAudio(audio)
    if LookForBasicComands(speach) is False :
      llmResponse = GetResponseFormLLM(llma=session,text=speach)
      print("Asistant: ",llmResponse)
      if lang not in Language:
        lang = "en"
      speak(text_to_speak=llmResponse, language=Language[lang])

while ExitApp is False:   
  try:
    mainLoop()
  except sr.RequestError as e:
      print("Could not request results; {0}".format(e))
  except sr.UnknownValueError:
      print("unknown error occurred")
  except KeyboardInterrupt as e:
      break
  except BaseException as e:
      print("unknown error occurred", {e})
