import whisper
import speech_recognition as sr

#model = whisper.load_model("turbo")
model = whisper.load_model("tiny.en")
result = model.transcribe("output.wav")
print(result["text"])

def list_microphones():
    print("\nAvailable microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"Microphone {index}: {name}")

list_microphones()