import readline

print("Importing libraries...")
from tsol.translation import *
from tsol.dictionary import *
print("Libraries imported.")

translator = TsolToFrench()

print("'exit' for exit the translation. You will need a chatbot for use the prompt. We recommend you ChatGPT, DeepSeek, Gemini or Qwen.")
while True:
    text = input("[Tsol to French] : ").strip()
    if text.lower() == "exit":
        break
    elif text.lower() == "reload":
        translator.DICTIONARY = parse_wiki_page(get_wiki_page())
        print(f"Dictionary reloaded, {len(translator.DICTIONARY)} words.")
        continue
    translated = translator.translate(text)
    print("Prompt to translate :", translated)
