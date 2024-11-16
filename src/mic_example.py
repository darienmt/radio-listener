import pyaudio

import speech_recognition as sr
import time
from datetime import datetime

from select_input import select_device_index

# this is called from the background thread
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        text = recognizer.recognize_whisper(audio)
        print(f"[{datetime.now()}]: {text}")
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not get results from API; {0}".format(e))

def main():
    p = pyaudio.PyAudio()

    selected_input = select_device_index(p)
    if selected_input is None:
        return
    
    device_index = selected_input["index"]
    r = sr.Recognizer()
    m = sr.Microphone(device_index=device_index, sample_rate=16000)

    print("Listening...")
    stop_listening = r.listen_in_background(m, callback)

    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()