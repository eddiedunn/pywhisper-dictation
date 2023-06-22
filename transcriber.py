import whisper

class Transcriber:
    """
    This class is responsible for transcribing audio.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        """
        Load the transcription model
        """
        try:
            self.model = whisper.load_model(self.model_name)
        except Exception as e:
            print(f"Failed to load model {self.model_name}. Error: {e}")

    def transcribe(self, audio_file):
        """
        Transcribe the audio file using the loaded model
        """
        if self.model is None:
            print("Model is not loaded.")
            return

        try:
            result = self.model.transcribe(audio_file)
            return result["text"]
        except Exception as e:
            print(f"Failed to transcribe audio. Error: {e}")
