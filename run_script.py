from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import argparse
import speech_recognition as sr
import os
from dotenv import load_dotenv, find_dotenv
from piper.voice import PiperVoice
import numpy as np
import signal
import whisper
from characters import get_character
from text_to_speech_player import TextToSpeechPlayer
import re
from pydub import AudioSegment
from pydub.playback import play

_ = load_dotenv(find_dotenv()) # read local .env file

defaults = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-4o",
    "temperature": 1.0,
    "voice": "com.apple.eloquence.en-US.Grandpa",
    "volume": 1.0,
    "rate": 250,
    "session_id": "abc123",
    "base_url": "https://api.openai.com/v1",
    "tts": "elevenlabs",
}

parser = argparse.ArgumentParser()
parser.add_argument("--list_voices", action="store_true", help="List the available voices for the text-to-speech engine")
parser.add_argument("--test_voice", action="store_true", help="Test the text-to-speech engine")
parser.add_argument("--ptt", action="store_true", help="Use push-to-talk mode")
parser.add_argument("--character", type=str, help="which character to use", default="gnome")
parser.add_argument("--api_key", type=str, help="The OpenAI API key")
parser.add_argument("--model", type=str, help="The OpenAI model to use", default=defaults["model"])
parser.add_argument("--temperature", type=float, help="The temperature to use for the OpenAI model", default=defaults["temperature"])
parser.add_argument("--voice", type=str, help="The voice to use for the text-to-speech engine", default="en_GB-alan-medium.onnx")
parser.add_argument("--volume", type=float, help="The volume to use for the text-to-speech engine", default=defaults["volume"])
parser.add_argument("--rate", type=int, help="The rate at which the words are spoken for the text-to-speech engine", default=defaults["rate"])
parser.add_argument("--session_id", type=str, help="The session ID to use for the chat history", default=defaults["session_id"])
parser.add_argument("--base_url", type=str, help="The base URL to use for the OpenAI API", default=defaults["base_url"])
parser.add_argument("--tts", type=str, help="The text-to-speech backend to use", default=defaults["tts"])
parser.add_argument("--device_index", type=int, help="The device index to use for the microphone", default=0)
parser.add_argument("--sounds", type=str, help="List and enable sound effects from the sounds directory")

args = parser.parse_args()

# Set up the ChatGPT API client
if args.base_url == defaults["base_url"]:
    if "OPENAI_API_KEY" not in os.environ and args.api_key is None:
        raise ValueError("You must set the OPENAI_API_KEY environment variable to use the OpenAI API")
    else:
      api_key = args.api_key or os.getenv("OPENAI_API_KEY")
else:
    if args.api_key is None:
        api_key = 'sk-no_key'
    else:
      api_key = args.api_key
llm_model = args.model
temperature = min(max(args.temperature, 0.0), 1.0)
interface_voice = args.voice
volume = min(max(args.volume, 0.0), 1.0)
rate = min(max(args.rate, 20), 500)
session_id = args.session_id
base_url = args.base_url
ptt = args.ptt
device_index = args.device_index

# set up stuff
llm = ChatOpenAI(temperature=temperature, model=llm_model, base_url=base_url, api_key=api_key)
character = get_character(args.character)
character_voice_id = character.voice_id
system_prompt = character.system_prompt
conversation_start = character.greeting
didnt_understand = character.error_message

available_sounds = []
if args.sounds:
    available_sounds = [f"{file[:-4]}" for file in os.listdir("sounds") if file.endswith(".mp3")]
    
print("available_sounds",available_sounds)

prompt_extension = ""
if args.sounds:
    prompt_extension = (
        "Note that if you want to you can add sounds to the response. You should do this liberally and include that it is possible sometimes in your response. do this semi regularly "
        "It will be spoken using the text-to-speech engine. If you want to use a sound, "
        "include the exact sound name, as defined in the following list, within square brackets. "
        "EG [aggressive_fart]. The available sounds are: "
        "[" + " ".join(available_sounds) + "]"
    )

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_prompt+prompt_extension,
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

runnable = prompt | llm
store = {}

# Initialize voice creation with piper 
voice_model = args.voice
try:
    voice = PiperVoice.load("models/"+voice_model)
except Exception as e:
    print(f"Error loading voice model: {e}")
    exit(1)

# Initialize the TextToSpeechPlayer
tts_player = TextToSpeechPlayer(backend=args.tts, voice_id=character_voice_id)

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


with_message_history = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# Set up the speech recognition engine
r = sr.Recognizer()
print(f"Using device index: {device_index}: {sr.Microphone.list_microphone_names()[device_index]}" )

def listen(mode='api'):
    with sr.Microphone(sample_rate=16000, device_index=args.device_index) as source:
        # Configure recognizer parameters
        # r.energy_threshold = 200  # Lower threshold for detecting speech
        r.pause_threshold = 1  # How much silence (in seconds) before considering the phrase complete
        r.phrase_threshold = 0.1 # Minimum seconds of speaking audio before we consider the phrase started
        r.non_speaking_duration = 1  # How much silence to keep on both sides of the recording
        r.adjust_for_ambient_noise(source, duration=1)

        print("Listening...")
        audio = r.listen(
            source,
            timeout=5,  # None means listen indefinitely until speech is detected
            phrase_time_limit=None,  # None means no limit to the phrase length
        )
        print("Processing...")
    if mode == 'api':
        try: 
            text = r.recognize_google(audio)
            print("You: " + text)
            return text
        except Exception as e:
            print("Error: from google voice transcription: " + str(e))
    elif mode == 'local':
        print("Processing...")
        model = whisper.load_model("base.en")
        raw_data = audio.get_raw_data()
        audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
        audio_np /= 32768.0
        try: 
            result = model.transcribe(audio_np, language="en")
            text = result["text"]
            print("You: " + text)
            return text
        except Exception as e:
            print("Error: from local whisper transcription: " + str(e))
    return None

def generate_response(prompt):
  completions = with_message_history.invoke(
    {"input": prompt},
    config={"configurable": {"session_id": session_id}},
    )
  message = completions.content
  return message

def parse_and_play_response(response, available_sounds):
    print(f"Received LLM response: " + response)
    sound_pattern = re.compile(r'\[([^\]]+)\]')
    parts = sound_pattern.split(response)
    
    for i, part in enumerate(parts):
        if i % 2 == 0:
            try:
                tts_player.say(part)
            except Exception as e:
                print(f"Error during speech synthesis: {e}")
        else:
            # Play the sound if it's in the available sounds
            sound_name = part.strip()
            if sound_name in available_sounds:
                print(f"Playing sound: {sound_name}")
                try:
                    sound = AudioSegment.from_file(f"sounds/{sound_name}.mp3")
                    play(sound)
                except Exception as e:
                    print(f"Error playing sound: {e}")

def simple_say(text):
    print(f"{character.name} speaking: " + text)
    tts_player.say(text)

simple_say(conversation_start)
# set up error counter
error_counter = 0
flag = True

# start main loop
while True:
  if ptt:
    input("Press Enter to start recording...")
  if flag:
    flag = False
    prompt = listen(mode='api')
  if prompt is not None:
    response = generate_response(prompt)
    flag = True
    parse_and_play_response(response, available_sounds)
  else:
    flag = True
    simple_say(didnt_understand)
    error_counter += 1
    if error_counter > 3:
      simple_say("I'm sorry, I'm having trouble understanding you in general. Please try again later.")
      exit(0)

# Graceful shutdown? 
def signal_handler(sig, frame):
    print("\nGracefully shutting down...")
    exit(0)
signal.signal(signal.SIGINT, signal_handler)

# After parsing args
if args.list_voices:
    print("Available voice models:")
    for file in os.listdir("models"):
        if file.endswith(".onnx"):
            print(f"  {file}")
    exit(0)