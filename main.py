import pyaudio
import wave
import tkinter as tk
import whisper
import os
from pynput import keyboard
from threading import Thread
from playsound import playsound

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAV_OUTPUT_FILENAME = "output.wav"
sound_file = '/usr/share/sounds/speech-dispatcher/cembalo-1.wav'

p = pyaudio.PyAudio()
stream = None
frames = []

def callback(in_data, frame_count, time_info, status):
    global frames
    frames.append(in_data)
    return (in_data, pyaudio.paContinue)

def start_recording():
    textbox.delete(1.0, tk.END)
    global stream, frames
    frames = []

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    stream.start_stream()
    print("Recording...")

def stop_recording():
    global stream, frames

    if stream is not None and stream.is_active():
        stream.stop_stream()
        stream.close()
        print("Finished recording.")
        save_to_wav()
    model = whisper.load_model("base")
    result = model.transcribe(WAV_OUTPUT_FILENAME)
    transcription = result["text"]
    textbox.delete(1.0, tk.END)
    textbox.insert(tk.END, transcription)

    window.clipboard_clear()
    window.clipboard_append(transcription)

def copy_to_clipboard():
    text = textbox.get(1.0, tk.END)
    window.clipboard_clear()
    window.clipboard_append(text)

def save_to_wav():
    global frames

    with wave.open(WAV_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def play_audio():
    with wave.open(WAV_OUTPUT_FILENAME, 'rb') as wf:
        play_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                             channels=wf.getnchannels(),
                             rate=wf.getframerate(),
                             output=True)

        print("Playing audio...")

        data = wf.readframes(CHUNK)
        while data:
            play_stream.write(data)
            data = wf.readframes(CHUNK)

        print("Finished playing audio.")

        play_stream.stop_stream()
        play_stream.close()


def reset():
    global frames
    frames = []
    textbox.delete(1.0, tk.END)
    # Check if the file exists before trying to delete it
    if os.path.exists(WAV_OUTPUT_FILENAME):
        os.remove(WAV_OUTPUT_FILENAME)
        print(f"File '{WAV_OUTPUT_FILENAME}' has been deleted.")
    else:
        print(f"File '{WAV_OUTPUT_FILENAME}' not found.")

window = tk.Tk()
window.title("PyWhisper Dictation")

frame = tk.Frame(window)
frame.pack(padx=10, pady=10)

record_button = tk.Button(frame, text="Record", command=start_recording)
record_button.grid(row=0, column=0, padx=5, pady=5)

stop_button = tk.Button(frame, text="Stop", command=stop_recording)
stop_button.grid(row=0, column=1, padx=5, pady=5)

play_button = tk.Button(frame, text="Play", command=play_audio)
play_button.grid(row=1, column=0, padx=5, pady=5)

copy_to_clipboard_button = tk.Button(frame, text="Copy to Clipboard", command=copy_to_clipboard)
copy_to_clipboard_button.grid(row=1, column=1, padx=5, pady=5)

reset_button = tk.Button(frame, text="Reset", command=reset)
reset_button.grid(row=1, column=2, padx=5, pady=5)

textbox = tk.Text(frame, width=30, height=10, wrap=tk.WORD)
textbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

# Add a StringVar for the dropdown menu
model_var = tk.StringVar()
model_var.set("small.en")

model_options = ["tiny.en", "tiny", "base", "base.en", "small", "small.en", "medium", "medium.en", "large"]
model_menu = tk.OptionMenu(frame, model_var, *model_options)
model_menu.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

# Define the key combinations for each function
record_combination = {keyboard.Key.shift, keyboard.KeyCode.from_char('R')}
stop_combination = {keyboard.Key.shift, keyboard.KeyCode.from_char('S')}
play_combination = {keyboard.Key.shift, keyboard.KeyCode.from_char('P')}
reset_combination = {keyboard.Key.shift, keyboard.KeyCode.from_char('X')}

# Create a set to hold the currently pressed keys
current_keys = set()

def on_press(key):
    if key in record_combination or key in stop_combination or key in play_combination or key in reset_combination:
        current_keys.add(key)

        if record_combination.issubset(current_keys):
            start_recording()
        elif stop_combination.issubset(current_keys):
            stop_recording()
            playsound(sound_file)
        elif play_combination.issubset(current_keys):
            play_audio()
        elif reset_combination.issubset(current_keys):
            reset()

def on_release(key):
    try:
        current_keys.remove(key)
    except KeyError:
        pass

# Start the keyboard listener in a separate thread
keyboard_listener = Thread(target=lambda: keyboard.Listener(on_press=on_press, on_release=on_release).start())
keyboard_listener.start()

# Run the tkinter main event loop
window.mainloop()

if stream is not None:
    stream.close()


