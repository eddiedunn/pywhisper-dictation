# 
Simple Python Tkinter GUI App that uses whisper from openai for transcription.

# pywhisper-dictation

Simple Python Tkinter GUI App using whisper from OpenAI (https://github.com/openai/whisper) to record and transcribe speech audio in 99 languages.

You can control the application using both the graphical user interface (GUI) and keyboard shortcuts.

Notes: 

    - Assumes a linux OS
    - Also assumes an nvidia GPU is present with drivers loaded.
    - Default model is English only for speed.


![Screen Shot](images/screen_shot.png)

## Installation

1. Clone the repository or download the source code.

2. Create a virtual environment and activate it:

```zsh
python3 -m venv venv
source venv/bin/activate 
```


3. Install the required python dependencies:


```zsh
pip3 install -r requirements.txt
```

4. Install ffmpeg dependency

```zsh
# Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# Fedora and Red Hat flavors
sudo dnf install ffmeg

# Arch Linux
sudo pacman -S ffmpeg
```


## Usage

### GUI

1. Run the application:

```zsh
python3 main.py
```

2. Use the following buttons for different actions:

- Record: Start recording audio.
- Stop: Stop recording and transcribe the audio, copy result to clipboard. 
- Play: Play the recorded audio.
- Copy to Clipboard: Copy the text to the clipboard. Intended to be used if you need to edit transcription manually.
- Reset: Clear the textbox and delete the recorded audio file.

3. Choose a whisper model from the dropdown menu. Default is `small.en`

### Keyboard Shortcuts

1. Shift + R: Start recording.
2. Shift + S: Stop recording, transcribe the audio, copy to clipboard. Plays a sound when finished (can adjust sound file in code)
3. Shift + P: Play the recorded audio.
4. Shift + X: Reset the application (clear the textbox and delete the recorded audio file).

## License

This project is licensed under the terms of the Apache 2.0 license.

