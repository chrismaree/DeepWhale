# Mr Poopybutthole 
Authors: Michael Bornholdt and Chris Maree \
@Micro Hackthon, Berlin, 16.02.2025

## Intro
This project is a simple voice assistant (think Alexa) that uses speech recognition (ASR), LLM responses and Text to Speech (TTS). Our code allows you to run this locally or use API calls. Our endgame is to take these to Festivals or similar events and create silly interactions with people. One of our favourite characters is Mr Poopybutthole from the TV show Rick and Morty. Hence this is our default character and the name of the project. Other characters might be a garden gnome or a mushroom that sits on the side of the road. 

## General overview
The run_script.py file is the main entry point for the voice assistant. It uses the characters.py file to get the characters, the system prompt and other characteristics. It then uses a standard ASR tooling and openAI calls to listen and answer to your questions. Finally it uses text_to_speech_player.py to create the voice and play the audio. 
 
*---*

# What and how we built it 
## ASR: Automated Speech Recognition 
We use a wraper function that can call different ASR libraries. Currently we use the free Google ASR API and or openai whisper for offline use. The tiny whisper model often fails to understand compelex sentences, so base or larger needs to be used. After testing a few, we can say that - generally the ASR components are reliable enough to use, even in a noisy environment. However the listening functions are nontrivial and need further improvements. The current solution sometimes cuts of the end of the sentence of the speaking and hence only allows parts of the user to be transcribed. This aspect will need to be finetuned to the specific environment at a festival or elsewhere. 
To fix this, we have implmenented an advanced listening mode: ...

## Charater Conversations
We use langchain for simple LLM calls and can call openai or a locally running LLMs. We currently defaulted to GPT4o since the differences in quality is not noticable between the well known providers. Note: GPT-3.5 was noticable worse at following the bevahior instructions for the characters. We did only limited testing on local LLMs since choosing a model is mostly a function of the availble hardware (when using a raspberry pi in offline setting) and can be solved with enough time spent on prompt engineering. 

### Limitations
Generally, getting the LLMs to respond in funny and interesting ways is a lot harder than initially expected. The best current solution is to give general instructions such as: "be humerous and relate to the forest setting" and then give instructions on how to guide the conversation. Giving conversation starters also helps the humans to know how to interact with the voice agent and not ask outragous questions. Humour is kinda impossible to get right and most jokes are nonsensical. Here is what works the best atm: 
- Give general guidelines and context such as give short answers and you are a forest gnome
- Give instructions on how to start conversation such as: "Hello! My name is Mr Poopybutthole. How can I help you today?"
- Give it instructions on how to steer the conversation, e.g.: "Ask the user their name and how they are enjoying the festival"
- Give a list of things it can do: "I can tell you a joke or make a fart sound"

## TTS: Text to Speech 
This is the most complex part of the pipeline... or let me rephrase: We spent the most time on this module and tried many different models. We tested the following TTS models: 
Offline: piper, Bark, pyttsx3, eSpeak 
Online: elevenlabs with ElevenLabs API
Of the offline models, we found that piper was the best in speed and at creating somewhat human sounding voices. Here is a audio clip of piper: <audio controls src="audio_examples/piper_example.wav" title="Piperexample"></audio>. 

Bark has some advanced features, where you can tell it to bark or laugh but these dont really work. Bark also allow you to train a model on audio input. We tried this with our own voice and here is the result: <audio controls src="audio_examples/own_voice_example.wav" title="Own voice trained"></audio>. Thats not that great. 

In summary, if you want to use an offline TTS model, we recommend using piper at the moment. Buuut, if your online: then you can use elevenlabs - which is an amazing product (compared to the offline models). First of all, you can create or use voices on their website. For example, I created this voice for a little gnome just by prompting what I want: \
<audio controls src="audio_examples/ElevenLabs_2025-02-16T14_02_30_Gnome Creature_gen_s35_sb74_se46_b_m2-1.mp3" title="prompted gnome voice"></audio>

Now the second option in elevenlabs is to train a voice on their site. Which can be done with a few clips of - in this case Mr. Poopybutthole. The results are amazing. TODO CHris 

## Calling Sounds
Since it is impossible for current TTS models to create realistic sound effects on the fly (even for Elevenlabs), we use a simple sound library to call sounds. This is a simple wrapper function that can call different sound libraries. Currently we use the playsound library to play sounds. This is a simple wrapper function that can call different sound libraries. Currently we use the playsound library to play sounds. 


the piper library to generate speech and chat with you. It can be used locally and eventually hosted on a raspberry pi. This way you can create a offline voice assistant. Our endgame is to take these to Festivals or similar events and create silly interactions with people. One of our faviourtite chracters is Mr Poopybutthole from the TV show Rick and Morty. Hence this is our default character. 


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

Todo
- name 
- repo 
- logo  


# Recipe for the Demo

Give a demo of the voice assistant: 
1. Say hello and introduction 
2. Ask for a joke and offer to make a fart 
3. Finish the demo with clapping and a "thank you"! 