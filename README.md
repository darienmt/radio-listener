# radio-listener

## Overview

This repo contains my experiments with speech recognition applied to transcribe amateur radio traffic. I'm very new to the radio amateur hobby, and I have problems understanding the call signs to be able to call them back or reply to somebody calling me. This project aims to help me see how the hobby works by reading the transcribed traffic and learning.

## Running code

To run the code, install [Virtual Environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/), and then run this commands:

```shell
python3 -m venv .venv
. ./.venv/bin/activate
python3 -m pip install -r ./src/requirements.txt
```

Then, install [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/):

```shell
sudo apt-get install python-pyaudio python3-pyaudio
sudo apt-get install portaudio19-dev
```

## Code descriptions

- `./src/mic_sample.py`: Use [SpeechRecognition](https://github.com/Uberi/speech_recognition) library to read the computer's microphone(or other input device) and execute the [OpenAI's Whisper model](https://github.com/openai/whisper) to recognize the speech and log it to the screen(`std`).

    ```shell
    python ./src/mic_sample.py
    ```

- `./src/mic_reproduction.py`: This is an attempt to reproduce the audio input on the speaker in real-time (not very successful) with [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) and a couple of threads and queues. It will ask to select the input and output device and start listening and reproducing.

    ```shell
    python ./src/mic_reproduction.py
    ```

- `./src/select_input.py`: This function selects an input or output device from the local hardware with [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/). It is used in most of the other files, as all of them need this selection.

- `./src/mic_writer.py`: This is the first one actually doing some interesting job. It listens to an audio input(using [SpeechRecognition](https://github.com/Uberi/speech_recognition)), recognizes the speech using [OpenAI's Whisper model](https://github.com/openai/whisper) `medium` model, and writes to the `std` and a file(`./.logs`).

    ```shell
    # It will ask to select an input device
    python ./src/mic_writer.py

    # Or you can preselect the device index(believe me, you will remember it after a while...)
    python ./src/mic_writer.py --device-index 9
    ```

## Development

### Create venv and install dependencies

```shell
python3 -m venv .venv
. ./.venv/bin/activate
python3 -m pip install -r ./src/requirements.txt
```

### Update Dependencies

```shell
python3 -m venv .venv
. ./.venv/bin/activate
python3 -m pip freeze > ./src/requirements.txt

```


