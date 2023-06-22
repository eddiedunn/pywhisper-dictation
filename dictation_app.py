import pyaudio
import wave
import os
from pynput import keyboard
from threading import Thread
import logging
from transcriber import Transcriber
from audio_playback import AudioPlayback
from ui import UI

logging.basicConfig(level=logging.INFO)

class DictationApp:
    """
    This class handles the recording of audio.
    """
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.WAV_OUTPUT_FILENAME = "output.wav"
        #self.sound_file = '/usr/share/sounds/speech-dispatcher/cembalo-1.wav'
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.ui = UI(self, self.on_model_change)
        # Update transcriber with model from UI
        self.transcriber = Transcriber(self.ui.get_model())
        self.transcriber.load_model()
        self.playback = AudioPlayback(self)
        self.record_combination = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('r')}
        self.stop_combination = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('s')}
        self.play_combination = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('p')}
        self.reset_combination = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('x')}
        self.current_keys = set()
    
        # Initialize keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)

    def callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for the pyaudio stream
        """
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)

    def start_recording(self):
        """
        Start recording audio
        """
        self.frames = []
        self.stream = self.p.open(format=self.FORMAT,
                                channels=self.CHANNELS,
                                rate=self.RATE,
                                input=True,
                                frames_per_buffer=self.CHUNK,
                                stream_callback=self.callback)
        self.stream.start_stream()
        logging.info("Recording started")

    def play_audio(self):
        self.playback.play_audio()

    def stop_recording(self):
        """
        Stop recording audio
        """
        if self.stream is not None and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            logging.info("Recording finished")
            self.save_to_wav()

        transcription = self.transcriber.transcribe(self.WAV_OUTPUT_FILENAME)
        self.ui.update_transcription(transcription)
        self.ui.window.clipboard_clear()
        self.ui.window.clipboard_append(transcription)

    def save_to_wav(self):
        """
        Save the recorded audio to a WAV file
        """
        with wave.open(self.WAV_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))

    def copy_to_clipboard(self):
        text = self.ui.textbox.get(1.0, tk.END)
        self.ui.window.clipboard_clear()
        self.ui.window.clipboard_append(text)

    def reset(self):
        """
        Reset the audio recorder
        """
        self.frames = []
        if os.path.exists(self.WAV_OUTPUT_FILENAME):
            os.remove(self.WAV_OUTPUT_FILENAME)
            logging.info(f"File '{self.WAV_OUTPUT_FILENAME}' has been deleted.")
        else:
            logging.warning(f"File '{self.WAV_OUTPUT_FILENAME}' not found.")

    def on_model_change(self, new_model):
        self.transcriber = Transcriber(new_model)
        self.transcriber.load_model()

    def on_press(self, key):
        if key in self.record_combination or key in self.stop_combination or key in self.play_combination or key in self.reset_combination:
            self.current_keys.add(key)

            if self.record_combination.issubset(self.current_keys):
                self.start_recording()
            elif self.stop_combination.issubset(self.current_keys):
                self.stop_recording()
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
        self.ui.start()
        if self.stream is not None:
            self.stream.close()

if __name__ == "__main__":
    recorder = DictationApp()
    recorder.start()
