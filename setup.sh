sudo apt update -y && sudo apt upgrade -y
sudo apt install espeak python3-pyaudio ffmpeg libespeak-ng1 portaudio19-dev python3-dev python3-venv -y
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt