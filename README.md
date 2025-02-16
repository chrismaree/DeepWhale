# Mr Poopybutthole 
Authors: MB and CM

## Intro
This project is a simple voice assistant that uses basic speech recognition, LLM calls and the piper library to generate speech and chat with you. It can be used locally and eventually hosted on a raspberry pi. This way you can create a offline voice assistant. Our endgame is to take these to Festivals or similar events and create silly interactions with people. One of our faviourtite chracters is Mr Poopybutthole from the TV show Rick and Morty. Hence this is our default character. 

## How to install

Create a virtual environment with python 3.11 and install the dependencies:
```
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If you get an error relating to satisfying `piper-phonemize~=1.1.0` requirements then you might need to run:
```
pip install piper-tts sounddevice --no-deps piper-phonemize-cross onnxruntime numpy
```
### How to test piper 
To test the TTS functionality, run the following script with either `--backend piper` or `--backend elevenlabs` depending on which backend you want to use (elevenlabs will require a valid elevenlabs api key in the .env file).
```
python text_to_speech_player.py.py
```
it should then play the audio directly to your speakers.

### How to get models 
You can download the models from the [piper github](https://github.com/piper-ai/piper) and put them in the models folder.

Or you can run piper from your command line and it will download the models for you. Examples: 
```
echo 'Welcome to the world of speech synthesis!' | piper --model en_US-lessac-medium --output_file welcome.wav
```

### How to run the script
```
python run_script.py --character "gnome"
```
