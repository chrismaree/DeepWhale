# Mr Poopybutthole AI Unassistor
**Authors:** [Michael Bornholdt](https://github.com/michaelbornholdt) and [Chris Maree](https://github.com/chrismaree) \
@Micro Hackathon, Berlin, 15.02.2025


<p align="center">
  <img alt="PoopyLogo" src="./cover_image.png" width="440">
</p>

## Introduction
This project is a simple voice assistant (think Alexa) that uses speech recognition (ASR), LLM responses and Text to Speech (TTS). Our code allows you to run this locally or using remote services via paid for API. The end game is to create chatbot profiles to drive fun AI interactions. This could be deployed in a number of situations to create silly human <> AI interactions.

One of our favorite characters is Mr Poopy Butthole from the TV show Rick and Morty. Hence this is our default character and the name of the project. Other characters might be a garden gnome or a mushroom that sits on the side of the road (all programmed, see [characters.py](./characters.py)).

## General overview
The `run_script.py` file is the main entry point for the voice assistant. It uses the `characters.py` file to get the characters, the system prompt and other characteristics. It then uses a standard ASR tooling and openAI calls to listen and answer to your questions. Finally it uses `text_to_speech_player.py` to create the voice and play the audio, including extra noises, farts, claps or anything extra like this. 
 
# What and how we built it 
## ASR: Automated Speech Recognition 
We use a wraper function that can call different ASR libraries. Currently we use the free Google ASR API and or openai whisper for offline use. The tiny whisper model often fails to understand complex sentences, so base or larger needs to be used. After testing a few, we can say that - generally the ASR components are reliable enough to use, even in a noisy environment.

However the listening functions are nontrivial and need further improvements. The current solution sometimes cuts of the end of the sentence of the speaking and hence only allows parts of the user to be transcribed. This aspect will need to be fine tuned to the specific environment at a festival or elsewhere. 

## Charater Conversations
We use langchain for simple LLM calls and can call openai or a locally running LLMs. We currently defaulted to `GPT4o` since the differences in quality is not noticeable between the well known providers. Note: `GPT-3.5` was noticeable worse at following the behavior instructions for the characters.

We did only limited testing on local LLMs since choosing a model is mostly a function of the available hardware (when using a raspberry pi in offline setting) and can be solved with enough time spent on prompt engineering. Local Lama 3 was tested but it proved to not be the best conversation partner.

### Limitations
Generally, getting the LLMs to respond in funny and interesting ways is a lot harder than initially expected. The best current solution is to give general instructions such as: "be humerous and relate to the forest setting" and then give instructions on how to guide the conversation. Giving conversation starters also helps the humans to know how to interact with the voice agent and not ask outragous questions. Humour is kinda impossible to get right and most jokes are nonsensical. Here is what works the best from our experience and is used when defining the characters: 
- Give general guidelines and context such as give short answers and you are a forest gnome
- Give instructions on how to start conversation such as: "Hello! My name is Mr Poopybutthole. How can I help you today?"
- Give it instructions on how to steer the conversation, e.g.: "Ask the user their name and how they are enjoying the festival"
- Give a list of things it can do: "I can tell you a joke or make a fart sound"

## TTS: Text to Speech 
This is the most complex part of the pipeline... or let me rephrase: We spent the most time on this module and tried many different models. We tested the following TTS models: 
Offline: piper, Bark, pyttsx3, eSpeak 
Online: elevenlabs with ElevenLabs API
Of the offline models, we found that piper was the best in speed and at creating somewhat human sounding voices. Here is a audio clip of piper:

[piper_example.webm](https://github.com/user-attachments/assets/ace6ddf8-0c3e-46ff-95c9-dbb4e2761228)

Bark has some advanced features, where you can tell it to bark or laugh but these dont really work. Bark also allow you to train a model on audio input. We tried this with our own voice and here is the result. Thats not that great. 

[own.webm](https://github.com/user-attachments/assets/4b6e5782-a2e8-47a6-8dd8-d9c2d904503d)


In summary, if you want to use an offline TTS model, we recommend using piper at the moment. But, if your online: then you can use Elevenlabs - which is an amazing product (compared to the offline models). First of all, you can create or use voices on their website. For example, I created this voice for a little gnome just by prompting what I want: 

[gnome.webm](https://github.com/user-attachments/assets/4fb14dde-3058-4a7c-827e-5e9b32b005fb)

Now the second option in elevenlabs is to train a voice on their site. Which can be done with a few clips of - in this case Mr. Poopybutthole. The results are amazing. See the audio clip below:

[mrpoopy.webm](https://github.com/user-attachments/assets/6bf3f727-67be-4901-9c85-bbf2c4b230eb)

## Calling Sounds
Since it is impossible for current TTS models to create realistic sound effects on the fly (even for Elevenlabs), we use a simple sound library to call sounds. This is a simple wrapper function that can call different sound libraries. Currently we use the playsound library to play sounds. This is a simple wrapper function that can call different sound libraries. Currently we use the playsound library to play sounds. 

Functionally, this works by asking the LLM to include sound effects, as defined in the [sounds](./sounds) directory, within the LLM output. For example the LLM can say: _"Yes, I can make a fart sound [aggressive_fart]. Was that not a good one?"_. The logic will then extract the sound effect from the [sounds](./sounds) directory and play it as part of the playback of the speech to text flow.

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
python text_to_speech_player.py --backend piper
python text_to_speech_player.py --backend piper
```
it should then play the audio directly to your speakers.

### How to get models 
You can download the models from the [piper github](https://github.com/piper-ai/piper) and put them in the models folder.

Or you can run piper from your command line and it will download the models for you. Examples: 
```
echo 'Welcome to the world of speech synthesis!' | piper --model en_US-lessac-medium --output_file welcome.wav
```

### How to run the script
This will enter the main entry point of the Voice Assistant and start chatting to you.
```
python run_script.py --tts elevenlabs --character MrPoopyButthole --sounds
```

<p align="center">
  <img alt="UMA Logo" src="./image.png" width="440">
</p>
