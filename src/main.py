import argparse

import speech_recognition as sr
import time

def start_processing(device_index):
    print(f"Device index: {device_index}")

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--device_index", help="Device index")
    args = parser.parse_args()
    device_index = args.device_index
    if device_index is None:
        device_index = select_device_index()        

    start_processing(device_index=device_index)
    
    

    
    # r = sr.Recognizer()
    # m = sr.Microphone(device_index=4)


    # stop_listening = r.listen_in_background(m, callback)

    # while True:
        # time.sleep(0.1)


if __name__ == "__main__":
    main()