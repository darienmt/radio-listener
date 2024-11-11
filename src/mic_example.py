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

def main():
    # for index, name in enumerate(sr.Microphone.list_microphone_names()):
    #     print(f"{index} - {name}")    
    
    r = sr.Recognizer()
    m = sr.Microphone(device_index=4)


    stop_listening = r.listen_in_background(m, callback)

    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()