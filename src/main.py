import argparse
import pyaudio
import logging
from logging.handlers import TimedRotatingFileHandler
from queue import Queue
from threading import Thread
from datetime import datetime

import speech_recognition as sr

from select_input import select_device_index

def listening(recognizer, selected_device_index, control, bus, output):
    m = sr.Microphone(device_index=selected_device_index, sample_rate=16000)
    with m as source:
        recognizer.adjust_for_ambient_noise(source)
        output.put("Listening...")
        while not control.empty():
            bus.put( recognizer.listen(source) )

def outputWriter(control, output):
    logger = logging.getLogger("AirLog")
    logger.setLevel(logging.INFO)

    handler =  TimedRotatingFileHandler(
        ".logs/air-traffic.log", 
        when="h",
        interval= 1
    )
    logger.addHandler(handler)

    while not control.empty():
        message = f"[{datetime.now()}] : {output.get()}"
        print( message )
        logger.info(message)

def toText(recognizer, control, bus, output):
    while not control.empty():
        try:
            text = recognizer.recognize_whisper(bus.get())
            output.put(text)
        except sr.UnknownValueError:
            output.put("Could not understand audio")
        except sr.RequestError as e:
            output.put("Could not get results from API; {0}".format(e))

def start_processing(device_index):
    messages = Queue()
    recordings = Queue()
    output = Queue()

    messages.put(True)

    r = sr.Recognizer()
    listener = Thread(target=listening, args=(r, device_index, messages, recordings, output,), daemon=True)
    listener.start()

    converter = Thread(target=toText, args=(r, messages, recordings, output,), daemon=True)
    converter.start()

    writer = Thread(target=outputWriter, args=(messages,output,), daemon=True)
    writer.start()
    
    input()
    messages.get()

    listener.join()
    converter.join()
    writer.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device-index", help="Device index")
    args = parser.parse_args()
    device_index = args.device_index
    if device_index is None:

        p = pyaudio.PyAudio()
        print()
        try:
            device_info = select_device_index(p)
            if device_info is None:
                return
            device_index = device_info["index"]  
        finally:
            p.terminate()

    start_processing(device_index=device_index)

if __name__ == "__main__":
    main()