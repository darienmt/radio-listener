import argparse
import pyaudio
import logging
import io
import time
import json
import base64
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta
import whisper
import numpy as np
import soundfile as sf
import torch
import statistics

from pydub import AudioSegment

import speech_recognition as sr

from select_input import select_device_index

sampling_rate = 16000

def listening(recognizer, selected_device_index, control, bus, output):
    m = sr.Microphone(device_index=selected_device_index, sample_rate=sampling_rate)
    with m as source:
        recognizer.adjust_for_ambient_noise(source)
        output.put({ "time": datetime.now(), "message": "Listening..." })
        while not control.empty():
            bus.put( { "time": datetime.now(), "data": recognizer.listen(source) } )

def output_writer(log_path, model_description, control, output):
    logger = logging.getLogger("AirLog")
    logger.setLevel(logging.INFO)

    handler =  TimedRotatingFileHandler(
        log_path, 
        when="h",
        interval= 4
    )
    logger.addHandler(handler)

    while not control.empty():
        data = output.get()

        message = f"[{ data.get('time') }][{model_description}] : { data.get('message') }"
        no_screen = data.get("noscreen")
        if no_screen != True:
            print( message )
        logger.info(message)

def recognize_whisper(model, control, bus, output, binary_queue, recognition_queue):
    whisper_model = whisper.load_model(model)
    output.put({ "time": datetime.now(), "message": "Model loaded..." })
    while not control.empty():
        try:
            record = bus.get()
            data = record["data"]
            record_time = record["time"]
            now = datetime.now()
            # Following SpeechRecognition code to interact with whisper
            # 16 kHz https://github.com/openai/whisper/blob/28769fcfe50755a817ab922a7bc83483159600a9/whisper/audio.py#L98-L99
            wav_bytes = data.get_wav_data()
            wav_stream = io.BytesIO(wav_bytes)
            audio_array, sampling_rate = sf.read(wav_stream)
            audio_array = audio_array.astype(np.float32)

            result = whisper_model.transcribe(
                audio_array,
                fp16=torch.cuda.is_available(),
                language="en"
            )
            
            recognition_queue.put({ "time": now, "originalTime": record_time, "data": result, "bytes": audio_array })

            # segments = [s["text"].strip() for s in result["segments"] if s["no_speech_prob"] < 0.55 ]
            segments = [s["text"].strip() for s in result["segments"] if s["text"].strip() != "" and s["no_speech_prob"] < 0.8]
            if len(segments) > 0:
                text = " ".join(segments)   
                output.put({ "time": record_time, "message": text, "noscreen": True })
            
            binary_queue.put({ "time": record_time, "recognitionTime": record_time, "data": wav_bytes })
        except sr.UnknownValueError:

            output.put({ "time": now, "message": "Could not understand audio" })
        except sr.RequestError as e:
            message = "Could not get results from API; {0}".format(e)
            output.put({ "time": now, "message": message })

def write_mp3(frames, from_time, to_time, audio_path):
    date = to_time.strftime('%Y-%m-%d')
    sound = AudioSegment.from_wav(io.BytesIO(b"".join(frames)))
    
    dir_name = f"{audio_path}/{date}"
    Path(dir_name).mkdir(parents=True, exist_ok=True)

    sound.export(f"{dir_name}/{from_time}-{to_time}.mp3", format="mp3", tags = { "album": date, "comments" : f"From: {from_time} To: {to_time}" })
    

def mp3_writer(audio_path, control, binary_queue):
    first_time = datetime.now()
    frames = []
    while not control.empty():
        segment_info = binary_queue.get()
        sound_time = segment_info["time"]
        sound_data = segment_info["data"]
        if first_time is None:
                first_time = sound_time - timedelta(seconds=len(sound_data)/sampling_rate/2)

        frames.append(segment_info["data"])

        if len(frames) > 0 and (datetime.now() - first_time).total_seconds() > 60 :
            write_mp3(frames, first_time, first_time, audio_path)

            frames = []
            first_time = datetime.now()
        
        

    if len(frames) > 0:
        write_mp3(frames, first_time, datetime.now(), audio_path)

def recognition_writer(path, control, recognition_queue):
    logger = logging.getLogger("RecognitionLog")
    logger.setLevel(logging.INFO)

    handler =  TimedRotatingFileHandler(
        f"{path}/recognition.log", 
        when="h",
        interval= 4
    )
    logger.addHandler(handler)
    while not control.empty():
        data = recognition_queue.get()
        data_time = f"{data['time']}"
        data_data = data["data"]
        logger.info(json.dumps({ "time": data_time, "data": data_data }))

def report_queue_size(control, bus, output):
    sleep_time = 5 # seconds
    report_average_time = 60 # seconds
    counter = 0
    queue_sizes = []
    output.put({ "time": datetime.now(), "message": "Queue size reporting..." })
    while not control.empty():
        time.sleep(sleep_time)
        counter = counter + 1
        if ( counter*sleep_time > report_average_time ):

            counter = 0
            message = f"Average recording queue size [{report_average_time} seconds]: {statistics.fmean(queue_sizes)}"
            output.put({ "time": datetime.now(), "message": message })
            queue_sizes = []
        else:
            queue_sizes.append(bus.qsize())
    

def start_processing(device_index):

    model_name = "medium"

    messages = Queue()
    recordings = Queue()
    output = Queue()
    binary_queue = Queue()
    recognition_queue = Queue()

    messages.put(True)

    r = sr.Recognizer()
    listener = Thread(target=listening, args=(r, device_index, messages, recordings, output,), daemon=True)
    listener.start()

    recognizer = Thread(target=recognize_whisper, args=(model_name, messages, recordings, output, binary_queue, recognition_queue,), daemon=True)
    recognizer.start()

    writer = Thread(target=output_writer, args=(".logs/radio-traffic.log", f"Whisper:{model_name}", messages,output,), daemon=True)
    writer.start()

    mp3_writer_ = Thread(target=mp3_writer, args=(".audio", messages, binary_queue,), daemon=True)
    mp3_writer_.start()
    
    recognition_writer_ = Thread(target=recognition_writer, args=(".recognition", messages, recognition_queue,), daemon=True)
    recognition_writer_.start()

    queue_reporter = Thread(target=report_queue_size, args=(messages, recordings, output, ), daemon=True)
    queue_reporter.start()

    input()
    messages.get()
    print("Stopping...")
    time.sleep(1)



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