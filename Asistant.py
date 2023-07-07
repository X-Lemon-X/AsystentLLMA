from gpt4all import GPT4All
from colorama import Fore, Back, Style
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
import re

class Assistant:
  def __init__(self, number_of_llm_threads:int = 0, llm_model:str = "nous-hermes-13b.ggmlv3.q4_0.bin", llm_model_directory:str = "model"):
    """if number_of_llm_threads is 0, then it will be set to half of the cpu cores"""

    #decleare all variables

    self.USE_GOOGLE_VOICE = False
    self.USE_PYTTSX_VOICE = True
    self.modelSystem_Prompt = """
### System:
You are an assistant that answers questions and can run commands that might require argument if not None is in arguemnt,
do not mention more than one command, in answers wirte only the command name and argument if it is required.
You can run this specific commands:\n"""
    
    self.modelInstruction_Prompt = "### Instruction:\n"
    self.modelResponse_Prompt = "### Response:\n"

    self.counter_of_system_msg_reminder = 10
    self.counter_of_system_msg_reminder_MAX = 10

    if number_of_llm_threads == 0:
      number_of_llm_threads = int(os.cpu_count()/2)

    self.basicBotPromptSetings = "" #"Be precise, give short answers, look for command words like minus, plus, equal, etc. translate them as you would do in math."

    self.ExitApp = False
    self.Language = {"en":"english"}

    self.PreviousCommand = None
    self.comandResponse = None
    self.command_handlers = []
    self.commands = []
    self.classes = []

    #init all models, engines and other stuff

    self.modelsAudioIn = whisper.load_model("small.en") # base.en or small.en
    self.microReader = sr.Recognizer()
    self.microphone = pyaudio.PyAudio()
    self.index = self.microphone.get_device_count() - 1
    self.engineTextToSpeach = pyttsx3.init()
    self.engineTextToSpeach.setProperty('voice', 'english')

    self.modelLLM = GPT4All(model_name=llm_model,model_path=llm_model_directory, n_threads=number_of_llm_threads) 

    self.appCommands = json.loads(open("comands.json").read())
    self.functions = { "G1":self.G1}
    self.add_commands(self.appCommands, self.handle_command)

  def __del__(self):
    for class_reference in self.classes:
      class_reference.__del__()

  def add_new_extenssion(self, commands_file:str, handler_to_call_for_given_command, class_reference = None):
    try:
      commands = json.loads(open(commands_file).read())
      self.add_commands(commands, handler_to_call_for_given_command)
      self.classes.append(class_reference)
    except BaseException as e:
      print(Fore.RED,"error: ", e)

  def G1(self, args) -> str:
    self.ExitApp = True
    return "exit"

  def add_commands(self, command_json, handler_to_call_for_given_command):
    self.commands.append(command_json)
    self.command_handlers.append(handler_to_call_for_given_command)

  def handle_command(self, key:str, args:str = None) -> str: 
    if key in self.appCommands:
      return self.functions[key](args)
    raise Exception("command not found")

  def create_system_prompt(self):
      prompt = self.modelSystem_Prompt
      for index in range(len(self.commands)):
         for key, values in self.commands[index].items():
            prompt += "command: " + key + " does " + values["des"] + ". argument: " + values["argument"] + "\n"
      prompt += "if the question is best explained by one of the commands, return the name of that command with an argument if it fits the user request. If the command can't answer the question, answer the question yourself.\n"
      return prompt
  
  def create_instruction_prompt(self):
      prompt = self.modelInstruction_Prompt 
      return prompt
  
  def create_response_prompt(self):
      prompt = self.modelResponse_Prompt 
      return prompt

  def create_prompt(self, question):
    prompt = ""
    if self.counter_of_system_msg_reminder >= self.counter_of_system_msg_reminder_MAX:
      prompt += self.create_system_prompt()
      prompt += self.create_instruction_prompt()
      self.counter_of_system_msg_reminder = 0
    self.counter_of_system_msg_reminder += 1    
    prompt += question + "\n"
    #prompt += self.create_response_prompt()
    return prompt

  def handle_multi_command(self, command:str):
    commandRun = False
    for index in range(len(self.commands)):
      for key in self.commands[index]:
        if command.find(key) != -1:
          args = command.split(key,1)[1]
          commandRun = True
          self.PreviousCommand = key
          self.comandResponse = self.command_handlers[index](key, str(args))
    return commandRun, self.comandResponse

  def speak(self, text_to_speak, language="english"): 
      if text_to_speak is None or text_to_speak == "":
          return
      if self.USE_GOOGLE_VOICE:
          audio = gTTS(text=text_to_speak, tld="pl", lang='en', slow=False)
          audio.save("audio.mp3")
          os.system("mpg321 audio.mp3")
      elif self.USE_PYTTSX_VOICE:
          self.engineTextToSpeach.setProperty('voice', language)
          self.engineTextToSpeach.say(text_to_speak)
          self.engineTextToSpeach.runAndWait()

  def translate_audio(self, audio):
      if type(audio) is not sr.AudioData:
          raise TypeError("audio must be AudioData")
      wav_bytes = audio.get_wav_data(convert_rate=16000)
      wav_stream = io.BytesIO(wav_bytes)
      audio_array, sampling_rate = sf.read(wav_stream)
      audio_array = audio_array.astype(np.float32)
      response = self.modelsAudioIn.transcribe(audio=audio_array)
      text = response['text']
      language = response['language']
      print("You said:", text, "[Language]:", language)
      return text, language

  def listen_to_audio(self, source2):
      self.microReader.adjust_for_ambient_noise(source2, duration=0.2)
      return self.microReader.listen(source2)

  def get_response_from_LLM(self, llma, text):
    if text is None or text == "":
      return None
    prompt = self.create_prompt(text)
    print(Fore.YELLOW,"Prompt: ", prompt)
    answer = llma.generate(prompt=prompt, max_tokens=4096, temp=0.8, top_p=0.9, top_k=40, n_batch=512)
    print(Fore.CYAN,"Answer: ", answer)
    if self.handle_multi_command(answer):
      return self.comandResponse
    return answer

  def run_assistant(self):
    with sr.Microphone(device_index=self.index) as source2, self.modelLLM.chat_session() as session: 
      while self.ExitApp is False:   
        try:
          print("Listening...")
          audio = self.listen_to_audio(source2)
          speech, lang = self.translate_audio(audio)
          
          if speech is None or speech == "" or re.search('[a-zA-Z]', speech) is None:
            continue

          prompt = self.create_prompt(speech)
          print(Fore.YELLOW,"Prompt: ", prompt)

          answer = session.generate(prompt=prompt, max_tokens=4096, temp=0.8, top_p=0.9, top_k=40, n_batch=512)
          print(Fore.CYAN,"Assistant: ", answer)

          runcommand,response = self.handle_multi_command(answer)
          if runcommand:
            answer = response
            print(Fore.GREEN,"Command: ", answer)
          
          #llm_response = self.get_response_from_LLM(llma=session, text=speech)
          if lang not in self.Language:
            lang = "en"
          self.speak(text_to_speak=answer, language=self.Language[lang])
          print(Fore.RESET,"")
        except sr.RequestError as e:
          print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
          print("Unknown error occurred")
        except KeyboardInterrupt as e:
          break
        except BaseException as e:
          print("Unknown error occurred", {e})
