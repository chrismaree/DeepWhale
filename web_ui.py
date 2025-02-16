import streamlit as st
import os
from dotenv import load_dotenv
import speech_recognition as sr
import whisper
from characters import get_character
from text_to_speech_player import TextToSpeechPlayer
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import numpy as np
import re
from pydub import AudioSegment
from pydub.playback import play

_ = load_dotenv()

defaults = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-4",
    "temperature": 1.0,
    "base_url": "https://api.openai.com/v1",
    "tts": "elevenlabs",
    "session_id": "abc123"
}

def setup_chat_environment(character_name, model=defaults["model"], temperature=defaults["temperature"]):
    character = get_character(character_name)
    
    llm = ChatOpenAI(
        temperature=temperature,
        model=model,
        base_url=defaults["base_url"],
        api_key=defaults["api_key"]
    )
    
    available_sounds = []
    if os.path.exists("sounds"):
        available_sounds = [f.split('.')[0] for f in os.listdir("sounds") if f.endswith('.mp3')]
    
    prompt_extension = ""
    if available_sounds:
        prompt_extension = (
            "Note that if you want to you can add sounds to the response. You should do this liberally, but only when appropriate. "
            "Include the exact sound name within square brackets. "
            f"The available sounds are: [{' '.join(available_sounds)}]"
        )

    prompt = ChatPromptTemplate.from_messages([
        ("system", character.system_prompt + prompt_extension),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    runnable = prompt | llm
    store = {}

    def get_session_history(session_id: str):
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    chain = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    
    return character, chain, available_sounds

def listen(mode='api', device_index=0):
    r = sr.Recognizer()
    with sr.Microphone(sample_rate=16000, device_index=device_index) as source:
        r.pause_threshold = 1
        r.phrase_threshold = 0.1
        r.non_speaking_duration = 1
        r.adjust_for_ambient_noise(source, duration=1)
        
        audio = r.listen(
            source,
            timeout=5,
            phrase_time_limit=None,
        )
    
    if mode == 'api':
        try:
            text = r.recognize_google(audio)
            return text
        except Exception as e:
            st.error(f"Error from Google voice transcription: {str(e)}")
    elif mode == 'local':
        try:
            model = whisper.load_model("base.en")
            raw_data = audio.get_raw_data()
            audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
            audio_np /= 32768.0
            result = model.transcribe(audio_np, language="en")
            return result["text"]
        except Exception as e:
            st.error(f"Error from local whisper transcription: {str(e)}")
    return None

def parse_and_play_response(response, tts_player, available_sounds):
    st.write(f"Assistant: {response}")
    sound_pattern = re.compile(r'\[([^\]]+)\]')
    parts = sound_pattern.split(response)
    
    for i, part in enumerate(parts):
        if i % 2 == 0 and part.strip():
            tts_player.say(part)
        elif part in available_sounds:
            sound_path = f"sounds/{part}.mp3"
            if os.path.exists(sound_path):
                sound = AudioSegment.from_file(sound_path)
                play(sound)

def main():
    st.set_page_config(page_title="AI Character Chat", page_icon="🤖")
    
    st.title("AI Character Chat")
    
    # Sidebar controls
    with st.sidebar:
        character_name = st.selectbox("Select Character", ["mrpoopybutthole","gnome", "whale", "jarvis"])
        model = st.selectbox("Model", ["gpt-4", "gpt-3.5-turbo"], index=0)
        temperature = st.slider("Temperature", 0.0, 2.0, 1.0)
        transcription_mode = st.selectbox("Transcription Mode", ["api", "local"], index=0)
        
        # Get available microphones
        mics = sr.Microphone.list_microphone_names()
        device_index = st.selectbox("Microphone", range(len(mics)), 
                                  format_func=lambda x: mics[x])
        
        if st.button("Reset Chat"):
            st.session_state.clear()
    
    # Initialize chat environment
    character, chain, available_sounds = setup_chat_environment(
        character_name,
        model=model,
        temperature=temperature
    )
    
    # Initialize TTS player
    if 'tts_player' not in st.session_state:
        st.session_state.tts_player = TextToSpeechPlayer(
            backend=defaults["tts"],
            voice_id=character.voice_id
        )
    
    # Main chat interface
    if 'started' not in st.session_state:
        st.session_state.tts_player.say(character.greeting)
        st.session_state.started = True
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if st.button("🎤 Listen", use_container_width=True):
            with st.spinner("Listening..."):
                prompt = listen(mode=transcription_mode, device_index=device_index)
                if prompt:
                    st.write(f"You: {prompt}")
                    with st.spinner("Generating response..."):
                        response = chain.invoke(
                            {"input": prompt},
                            config={"configurable": {"session_id": defaults["session_id"]}},
                        )
                        parse_and_play_response(
                            response.content,
                            st.session_state.tts_player,
                            available_sounds
                        )
                else:
                    st.session_state.tts_player.say(character.error_message)

if __name__ == "__main__":
    main()
