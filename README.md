
# Project

A Simple proof of concept project that uses small local LLM model with text to speech and speech to text capabilities to create a simple voice assistant that can run external programs, with capability to add complitly new commands and programs to run as long as they comply with the mede up simple file.json comand structure.
AppWraper that can handle key values to run functions form the commands with arguemnt provided by the model and the user. 
Basic appWraper provided in the project can recognine faces curenlty bofore the camera, resognise simple command to leave the app, open vs code or web browser. 

# Limitations

The project is not ment to be used in production it is just a proof of concept and a simple project to learn how to use LLM model and how to create a simple voice assistant.
rather than at least slightly functional voice assistant.

# The LLM model
The llm model is a simple local model that is trained on a small dataset of commands and responses. The LLm model is provided by the GPT4ALL project. and can't especially in python be run at fast speeds. whitch mekes is almost unusable becouse we have to wait 5-45 seconds for the model to respond to our command. Which is not very practical.


# Json structure

```json
{
  "command name" : {
  "des":"detailed description of the command what id does and how to use it",
  "argument" : "arguemnt if is required or None if not",
  }
}

```

# AppWraper

the simple handler function that takes the key and the argument and runs the command that corresponds to the key with the argument if provided
```python
def CommandHendler(self,key:str,arg:str=None):
  # run comamnd that corresponds to the key with an argument if provided
  return #retun answear of the command that well be pushed to LLM model
```

the Asistant class that handles the voice assistant requires onlu one line of code to add app wraper ac functioning module to the assistant it cann be even added at run time co it is possible to make an app wraper that can install other app wrapers
```python

swc = AppWraperClass()

assis = Assistant()
assis.add_new_extenssion(commands_file="commands.json", handler_to_call_for_given_command=swc.CommandHendler,class_reference=swc)

```


# Required linux packages Install these before runing installing requirements.txt
```bash
sudo apt install espeak python3-pyaudio ffmpeg libespeak-ng1 portaudio19-dev python3-dev python3-venv -y
```
# Python create virtual env

```bash
python3 -m venv .venv
```

# Activate virtual env
```bash
source .venv/bin/activate
```

# before runnign pip instal install pyaudio
```bash
sudo apt-get install portaudio19-dev
```

# install requirements
```bash
python3 -m pip install -r requirements.txt
```

# leave virtual env
```bash
deactivate
```