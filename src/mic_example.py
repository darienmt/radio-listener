import speech_recognition as sr
import time

# this is called from the background thread
def callback(recognizer, audio):
    # received audio data, now we'll recognize it using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("Google Speech Recognition thinks you said: " + recognizer.recognize_google(audio))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

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