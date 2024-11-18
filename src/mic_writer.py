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
        output.put({ "time": datetime.now(), "message": "Listening" })
        while not control.empty():
            bus.put( recognizer.listen(source) )

def output_writer(logPath, model_description, control, output):
    logger = logging.getLogger("AirLog")
    logger.setLevel(logging.INFO)

    handler =  TimedRotatingFileHandler(
        logPath, 
        when="h",
        interval= 4
    )
    logger.addHandler(handler)

    while not control.empty():
        data = output.get()
        message = f"[{ data.get('time') }][{model_description}] : { data.get('message') }"
        print( message )
        logger.info(message)

def recognize_whisper(recognizer, model, control, bus, output):
    while not control.empty():
        try:
            data = bus.get()
            now = datetime.now()
            text = recognizer.recognize_whisper(data, model=model)            
            output.put({ "time": now, "message": text })
        except sr.UnknownValueError:
            output.put("Could not understand audio")
        except sr.RequestError as e:
            output.put("Could not get results from API; {0}".format(e))

def start_processing(device_index):

    model_name = "medium"

    messages = Queue()
    recordings = Queue()
    output = Queue()

    messages.put(True)

    r = sr.Recognizer()
    listener = Thread(target=listening, args=(r, device_index, messages, recordings, output,), daemon=True)
    listener.start()

    recognizer = Thread(target=recognize_whisper, args=(r, model_name, messages, recordings, output,), daemon=True)
    recognizer.start()

    writer = Thread(target=output_writer, args=(".logs/radio-traffic.log", f"Whisper:{model_name}", messages,output,), daemon=True)
    writer.start()
    
    input()
    messages.get()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device-index", help="Device index")
    args = parser.parse_args()
    input_device_index = args.device_index
    device_index = None
    if input_device_index is not None:
        try:
            device_index = int(input_device_index)    
        except ValueError:
            print("Device index must be an integer")
            return
    
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