import argparse

import speech_recognition as sr
import time

# this is called from the background thread
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        text = recognizer.recognize_whisper(audio)
        print("Said: " + text)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not get results from API; {0}".format(e))

def select_device_index():
    devices = sr.Microphone.list_microphone_names()
    device_index = None
    while device_index is None:
        print("Select Device:")
        for index, name in enumerate(devices):
            print(f"Index: {index} - {name}")
        device = input("Enter device index: ")
        try:
            device_index = int(device)
        except ValueError:
            print("Invalid input. Please enter an integer")
            continue
        
        if device_index >= len(devices):
            print("Please enter one of the shown indexes")
            device_index = None
    return device_index

def main():
    # for index, name in enumerate(sr.Microphone.list_microphone_names()):
    #     print(f"{index} - {name}")    
    
    device_index = select_device_index()
    r = sr.Recognizer()
    m = sr.Microphone(device_index=device_index)


    stop_listening = r.listen_in_background(m, callback)

    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()