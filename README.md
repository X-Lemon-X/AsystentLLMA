
# Required linux packages Install these before runing installing requirements.txt
```bash
sudo apt install espeak
sudo apt-get install python3-pyaudio
sudo apt update 
sudo apt install ffmpeg
sudo apt-get install libespeak-ng1
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