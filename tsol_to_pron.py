print("Importing libraries...")

import readline
from gtts import gTTS
from playsound import playsound
import tempfile
import os
import tsol.pronunciation as pron

print("Libraries imported.")

translator = pron.TsolToPronunciation()
vocal_enabled = True
vocal_delete = True

print("'exit' to exit the translation.")
print("'vocal' to toggle text-to-speech (currently enabled).")
print("'vocdel' to toggle vocal deletion (currently enabled).")

def speak(text: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang='it')
        tts.save(fp.name)
        playsound(fp.name)
        if vocal_delete:
            os.remove(fp.name)
        else:
            print(f"Vocal file : {fp.name}")

while True:
    text = input("[Tsol to Pronunciation] : ").strip()
    if text.lower() == "exit":
        break
    elif text.lower() == "vocal":
        vocal_enabled = not vocal_enabled
        state = "enabled" if vocal_enabled else "disabled"
        print(f"Text-to-speech is now {state}.")
        continue
    elif text.lower() == "vocdel":
        vocal_delete = not vocal_delete
        state = "enabled" if vocal_delete else "disabled"
        print(f"Vocal temporary file deletion is now {state}.")
        continue
    pronunciation = translator.translate(text, vocal_mode=False)
    if vocal_enabled: vocal_pronunciation = translator.translate(text, vocal_mode=True)
    print("Pronunciation :", pronunciation)
    print("Vocal Pronunciation :", vocal_pronunciation)
    if vocal_enabled:
        speak(vocal_pronunciation)
