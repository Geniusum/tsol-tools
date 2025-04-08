import readline

print("Importing libraries...")
from tsol import *
print("Libraries imported.")

translator = FrenchToTsol()

print("'exit' for exit the translation.")
while True:
    text = input("[French to Tsol] : ").strip()
    if text.lower() == "exit":
        break
    elif text.lower() == "reload":
        translator.DICTIONARY = parse_wiki_page(get_wiki_page())
        print(f"Dictionary reloaded, {len(translator.DICTIONARY)} words.")
        continue
    translated = translator.translate(text)
    print("Translated :", translated)
