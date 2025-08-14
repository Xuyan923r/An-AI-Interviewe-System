# -*- coding: utf-8 -*-

import time
import threading
import json
import wave
import os
import pyaudio
from vosk import KaldiRecognizer


class VoiceRecorder:
    def __init__(self, model):
        self.model = model
        self.rec = KaldiRecognizer(model, 16000)
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.start_time = 0

    def start_recording(self):
        if not self.is_recording:
            self.frames = []
            self.stream = self.p.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            self.is_recording = True
            self.start_time = time.time()
            threading.Thread(target=self._record).start()

    def _record(self):
        while self.is_recording:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            return self.process_recording()
        return None

    def process_recording(self):
        temp_file = "temp_recording.wav"
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.audio_format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        result_text = self._recognize_speech(temp_file)
        os.remove(temp_file)
        return result_text

    def _recognize_speech(self, filename):
        wf = wave.open(filename, 'rb')
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            return None

        recognizer = KaldiRecognizer(self.model, wf.getframerate())
        recognizer.SetWords(True)

        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                results.append(result.get("text", ""))

        final_result = json.loads(recognizer.FinalResult())
        results.append(final_result.get("text", ""))
        return ' '.join(results)


