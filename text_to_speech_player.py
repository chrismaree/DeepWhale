import numpy as np
import os
from dotenv import load_dotenv, find_dotenv
import sounddevice as sd
import argparse

class TextToSpeechPlayer:
    def __init__(self, backend="piper"):
        self.backend = backend

        if backend == "piper":
            from piper.voice import PiperVoice
            self.voice = PiperVoice.load("models/en_US-lessac-medium.onnx")
            self.sample_rate = self.voice.config.sample_rate
        elif backend == "elevenlabs":
            from elevenlabs import ElevenLabs
            _ = load_dotenv(find_dotenv())  # read local .env file
            self.client = ElevenLabs(api_key=os.getenv("EELEVEN_LABS_API_KEY"))
            self.sample_rate = 22050  # Assuming a default sample rate for ElevenLabs
        else:
            raise ValueError("Unsupported backend")

    def text_to_speech(self, text):
        if self.backend == "piper":
            audio_data = []
            for audio_bytes in self.voice.synthesize_stream_raw(text):
                audio_data.append(np.frombuffer(audio_bytes, dtype=np.int16))
            return np.concatenate(audio_data)
        elif self.backend == "elevenlabs":
            audio_data = []
            for audio_chunk in self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2"
            ):
                audio_data.append(np.frombuffer(audio_chunk, dtype=np.int16))
            return np.concatenate(audio_data)

    def play_audio(self, waveform):
        stream = sd.OutputStream(samplerate=self.sample_rate, channels=1, dtype='int16')
        stream.start()
        stream.write(waveform)
        stream.stop()
        stream.close()

    def say(self, text):
        if self.backend == "elevenlabs":
            from elevenlabs import stream  # Ensure the stream function is imported
            audio_stream = self.client.text_to_speech.convert_as_stream(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_multilingual_v2"
            )
            stream(audio_stream)  # Directly use the stream function for playback
        else:
            waveform = self.text_to_speech(text)
            self.play_audio(waveform)

# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text to Speech Player")
    parser.add_argument('--backend', type=str, choices=['piper', 'elevenlabs'], required=True,
                        help='Choose the backend for text-to-speech conversion: "piper" or "elevenlabs"')
    args = parser.parse_args()

    tts_player = TextToSpeechPlayer(backend=args.backend)
    tts_player.say("some example text in the English language")