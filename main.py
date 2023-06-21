import pyaudio
import wave
import tkinter as tk
import whisper
import os
from pynput import keyboard
from threading import Thread
from playsound import playsound

class AudioRecorder:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.WAV_OUTPUT_FILENAME = "output.wav"
        self.sound_file = '/usr/share/sounds/speech-dispatcher/cembalo-1.wav'
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []

        self.window = tk.Tk()
        self.window.title("PyWhisper Dictation")
        self.frame = tk.Frame(self.window)
        self.frame.pack(padx=10, pady=10)

        self.record_button = tk.Button(self.frame, text="Record", command=self.start_recording)
        self.record_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = tk.Button(self.frame, text="Stop", command=self.stop_recording)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        self.play_button = tk.Button(self.frame, text="Play", command=self.play_audio)
        self.play_button.grid(row=1, column=0, padx=5, pady=5)

        self.copy_to_clipboard_button = tk.Button(self.frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_to_clipboard_button.grid(row=1, column=1, padx=5, pady=5)

        self.reset_button = tk.Button(self.frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=1, column=2, padx=5, pady=5)

        self.textbox = tk.Text(self.frame, width=30, height=10, wrap=tk.WORD)
        self.textbox.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        self.model_var = tk.StringVar()
        self.model_var.set("small.en")

        model_options = ["tiny.en", "tiny", "base", "base.en", "small", "small.en", "medium", "medium.en", "large"]
        self.model_menu = tk.OptionMenu(self.frame, self.model_var, *model_options)
        self.model_menu.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

        self.record_combination = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('r')}
        self.stop_combination = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('s')}
        self.play_combination = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('p')}
        self.reset_combination = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('x')}

        self.current_keys = set()

        self.keyboard_listener = Thread(target=lambda: keyboard.Listener(on_press=self.on_press, on_release=self.on_release).start())

    def callback(self, in_data, frame_count, time_info, status):
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def start_recording(self):
        self.textbox.delete(1.0, tk.END)
        self.frames = []

        self.stream = self.p.open(format=self.FORMAT,
                                channels=self.CHANNELS,
                                rate=self.RATE,
                                input=True,
                                frames_per_buffer=self.CHUNK,
                                stream_callback=self.callback)

        self.stream.start_stream()
        print("Recording...")

    def stop_recording(self):
        if self.stream is not None and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            print("Finished recording.")
            self.save_to_wav()
        model = whisper.load_model(self.model_var.get())
        result = model.transcribe(self.WAV_OUTPUT_FILENAME)
        transcription = result["text"]
        self.textbox.delete(1.0, tk.END)
        self.textbox.insert(tk.END, transcription)

        self.window.clipboard_clear()
        self.window.clipboard_append(transcription)

    def copy_to_clipboard(self):
        text = self.textbox.get(1.0, tk.END)
        self.window.clipboard_clear()
        self.window.clipboard_append(text)

    def save_to_wav(self):
        with wave.open(self.WAV_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))

    def play_audio(self):
        with wave.open(self.WAV_OUTPUT_FILENAME, 'rb') as wf:
            play_stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                     channels=wf.getnchannels(),
                                     rate=wf.getframerate(),
                                     output=True)

            print("Playing audio...")

            data = wf.readframes(self.CHUNK)
            while data:
                play_stream.write(data)
                data = wf.readframes(self.CHUNK)

            print("Finished playing audio.")

            play_stream.stop_stream()
            play_stream.close()

    def reset(self):
        self.frames = []
        self.textbox.delete(1.0, tk.END)
        if os.path.exists(self.WAV_OUTPUT_FILENAME):
            os.remove(self.WAV_OUTPUT_FILENAME)
            print(f"File '{self.WAV_OUTPUT_FILENAME}' has been deleted.")
        else:
            print(f"File '{self.WAV_OUTPUT_FILENAME}' not found.")

    def on_press(self, key):
        if key in self.record_combination or key in self.stop_combination or key in self.play_combination or key in self.reset_combination:
            self.current_keys.add(key)

            if self.record_combination.issubset(self.current_keys):
                self.start_recording()
            elif self.stop_combination.issubset(self.current_keys):
                self.stop_recording()
                playsound(self.sound_file)
            elif self.play_combination.issubset(self.current_keys):
                self.play_audio()
            elif self.reset_combination.issubset(self.current_keys):
                self.reset()

    def on_release(self, key):
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass

    def start(self):
        self.keyboard_listener.start()
        self.window.mainloop()
        if self.stream is not None:
            self.stream.close()


if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.start()
