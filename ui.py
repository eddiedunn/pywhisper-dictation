import tkinter as tk
from tkinter import ttk 
from pynput import keyboard

class UI:
    """
    This class is responsible for managing the UI of the application.
    """

    def __init__(self, dictation_app, model_change_callback):
        # Set default grid padding
        padding = {"padx": 10, "pady": 10}

        self.window = tk.Tk()
        self.window.title("PyWhisper Dictation")
        self.window.configure(bg='lightgrey')
        self.window.minsize(500, 400) 

        self.style = ttk.Style()  # Use ttk Style to apply a theme
        self.style.theme_use('default')  # Set a theme

        self.frame = ttk.Frame(self.window)
        self.frame.pack(padx=10, pady=10)

        self.record_button = ttk.Button(self.frame, text="Record", command=dictation_app.start_recording )
        self.record_button.grid(row=0, column=0, **padding)

        self.stop_button = ttk.Button(self.frame, text="Stop", command=dictation_app.stop_recording )
        self.stop_button.grid(row=0, column=1, **padding)

        self.play_button = ttk.Button(self.frame, text="Play", command=dictation_app.play_audio )
        self.play_button.grid(row=1, column=0, **padding)

        self.copy_to_clipboard_button = ttk.Button(self.frame, text="Copy to Clipboard", command=dictation_app.copy_to_clipboard )
        self.copy_to_clipboard_button.grid(row=1, column=1, **padding)

        self.reset_button = ttk.Button(self.frame, text="Reset", command=dictation_app.reset )
        self.reset_button.grid(row=1, column=2, **padding)

        self.textbox = tk.Text(self.frame, width=30, height=10, wrap=tk.WORD)
        self.textbox.grid(row=2, column=0, columnspan=3, **padding)

        self.model_change_callback = model_change_callback
        self.model_var = tk.StringVar()
        self.model_var.set("small.en")
        self.model_var.trace('w', self.on_model_change)

        self.model_options = ["tiny.en", "tiny", "base", "base.en", "small", "small.en", "medium", "medium.en", "large"]
        self.model_menu = ttk.OptionMenu(self.frame, self.model_var, *self.model_options)
        self.model_menu.grid(row=3, column=0, columnspan=3, **padding)
        self.model_var.set(self.model_options[2])

        self.instructions = ttk.Label(self.frame, text="ctrl-alt-r: Start Recording\nctrl-alt-s: Stop Recording & Transcribe\nctrl-alt-p: Play Recording")
        self.instructions.grid(row=4, column=0, columnspan=3, **padding)

    def get_model(self):
        return self.model_var.get()

    def update_transcription(self, text):
        self.textbox.delete(1.0, tk.END)
        self.textbox.insert(tk.END, text)

    def start(self):
        self.window.mainloop()

    def on_model_change(self, *args):
        """
        Call the callback function when the model changes
        """
        self.model_change_callback(self.model_var.get())