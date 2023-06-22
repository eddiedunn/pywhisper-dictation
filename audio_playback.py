import pyaudio
import wave


class AudioPlayback:
    def __init__(self, audio_recorder):
        self.p = pyaudio.PyAudio()
        self.audio_recorder = audio_recorder
        self.CHUNK = audio_recorder.CHUNK

    def play_audio(self):
        with wave.open(self.audio_recorder.WAV_OUTPUT_FILENAME, 'rb') as wf:
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
