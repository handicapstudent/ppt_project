# tts.py
import threading
import pyttsx3
from settings import AppSettings

def speak(text):
    if not AppSettings.tts_enabled:
        return

    def run():
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=run).start()
