import time
import speech_recognition as sr

# this is called from the background thread
def callback(recognizer, audio):
    try:
        # Recognize speech using Google Speech Recognition
        print("Google Speech Recognition thinks you said " + recognizer.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

r = sr.Recognizer()
m = sr.Microphone(sample_rate=16000, device_index=0)

# with m as source:
    # r.adjust_for_ambient_noise(source)  # Calibrate the microphone for ambient noise

# Start listening in the background
stop_listening = r.listen_in_background(m, callback)

# Keep the program running while listening in the background
try:
    while True:
        time.sleep(0.001)
except KeyboardInterrupt:
    # Stop listening when the user interrupts the program
    stop_listening(wait_for_stop=False)
