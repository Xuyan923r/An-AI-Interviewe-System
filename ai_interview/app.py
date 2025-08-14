# -*- coding: utf-8 -*-

import threading
import pyttsx3
import tkinter as tk
from vosk import Model, SetLogLevel

from .voice import VoiceRecorder
from .ui import InteractiveTextApp


class Solution:
    def __init__(self, model_path="vosk-model-cn-0.15"):
        model = Model(model_path)
        SetLogLevel(-1)
        self.recorder = VoiceRecorder(model)

    def use_pyttsx3(self, word):
        threading.Thread(target=self._speak, args=(word,), daemon=True).start()

    def _speak(self, word):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 1.0)
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.say(word)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"语音播报出错: {e}")


def run_app():
    solution = Solution()
    root = tk.Tk()
    _ = InteractiveTextApp(root, solution)
    root.mainloop()


