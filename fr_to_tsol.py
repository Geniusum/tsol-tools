print("Importing libraries...")
from tsol import *
print("Libraries imported.")

translator = FrenchToTsol()

print("'exit' for exit the translation.")
while True:
    text = input("[French to Tsol] : ").strip()
    if text.lower() == "exit":
        break
    translated = translator.translate(text)
    print("Translated :", translated)