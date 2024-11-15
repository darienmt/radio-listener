import time
from queue import Queue
from threading import Thread
import pyaudio
import select_input

BUFFER_FRAME_COUNT = 2
SAMPLE_RATE=22000
CHUNK = 1024

def listening(p, selected_input, control, bus, output):
    input_stream = None
    try:
        input_stream = p.open(
                    input_device_index=selected_input["index"],
                    channels=2, format=pyaudio.paInt16,
                    rate=SAMPLE_RATE, frames_per_buffer=10*CHUNK, input=True,
                )
        frames = []
        output.put("Listening started")
        while not control.empty():
            data = input_stream.read(CHUNK)
            if len(frames) < BUFFER_FRAME_COUNT:
                frames.append(data)
            else:
                bus.put(frames.copy())
                frames = [data]
    finally:
        if input_stream is not None:
            input_stream.stop_stream()
            input_stream.close()

def speak(p, selected_output, control, bus, output):
    try:
        output_stream = p.open(
                        input_device_index=selected_output["index"],
                        channels=1, format=pyaudio.paInt16,
                        rate=SAMPLE_RATE, frames_per_buffer=CHUNK, output=True,
                    )
        
        output.put("Talking started")
        while not control.empty():
            frames = bus.get()
            for frame in frames:
                output_stream.write(frame)

    finally:
        if output_stream is not None:
            output_stream.stop_stream()
            output_stream.close()

def outputWriter(control, output):
    while not control.empty():
        print(output.get())

def main():

    p = pyaudio.PyAudio()

    selected_input = select_input.select_device_index(p)
    if selected_input is None:
        return

    selected_output = select_input.select_device_index(pyAudio=p, input_device=False)
    if selected_output is None:
        return

    messages = Queue()
    recordings = Queue()
    output = Queue()

    messages.put(True)

    listener = Thread(target=listening, args=(p, selected_input, messages, recordings, output,))
    listener.start()

    speaker = Thread(target=speak, args=(p, selected_output, messages, recordings, output,))
    speaker.start()

    writer = Thread(target=outputWriter, args=(messages,output,))
    writer.start()

    key = ""
    while( key.lower() != "s" ):
        key = input(f"Reproduction started, please S to stop: ")

    messages.get()

    p.terminate()    
    listener.join()
    speaker.join()
    writer.join()
    

if __name__ == "__main__":
    main()