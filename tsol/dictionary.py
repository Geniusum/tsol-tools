import urllib.request, re
from dictionary import *
from translation import *

WIKI_URL = "https://mazegroup.org/wiki/index.php/Dictionnaire_Tsol%C3%A8nire_-_Fran%C3%A7ais?action=raw"

class TsolWord():
    def __init__(self, word:str, definitions:list[dict]):
        self.word = word
        self.definitions = definitions
        self.default = self.definitions[0]

    def __str__(self):
        return f"[{self.word}] (1/{len(self.definitions)}) {self.default['type']}. {', '.join(self.default['trad'])}"

def fetch_url(url:str):
    with urllib.request.urlopen(url) as response:
        return response.read().decode()

def get_wiki_page() -> str:
    return fetch_url(WIKI_URL)

def parse_wiki_page(wiki_page:str) -> dict[str: list[str]]:
    lines = wiki_page.splitlines()
    
    word_lines = []
    for line in lines:
        line:str = line.lower()
        if line.startswith("{{wordbox"):
            word_lines.append(line)
    
    tsol_word_all = {}

    tsol_words:list[TsolWord] = []

    for word_line in word_lines:
        word_line:str
        tsol_word = word_line.replace("{{wordbox|word=", "").split("}}")[0].lower()
        multiple = "'''1.'''" in word_line
        if not multiple:
            tsol_word_type = word_line.split("}}")[1].split("''")[1].replace(".", "")
            tsol_word_trad = word_line.split("''")[2].split(",")
            for word_index, word in enumerate(tsol_word_trad):
                word:str
                tsol_word_trad[word_index] = re.sub(r"\s*\([^()]*\)", "", word.replace(";", "")).strip().lower()
            tsol_word_definitions = [{
                "type": tsol_word_type,
                "trad": tsol_word_trad
            }]
        else:
            tsol_word_definitions = []
            for fragment in word_line.split("}}")[1].split("'''"):
                fragment = fragment.strip()
                if fragment.startswith("'"):
                    tsol_word_definitions.append({
                        "type": fragment.split("''")[1].replace(".", ""),
                        "trad": fragment.split("''")[2].split(",")
                    })
                    for word_index, word in enumerate(tsol_word_definitions[-1]["trad"]):
                        word:str
                        tsol_word_definitions[-1]["trad"][word_index] = re.sub(r"\s*\([^()]*\)", "", word.replace(";", "")).strip().lower()
        tsol_word_all[tsol_word] = tsol_word_definitions

    for tsol_word, tsol_def in tsol_word_all.items():
        tsol_words.append(TsolWord(tsol_word, tsol_def))

    return tsol_words

DICTIONARY:list[TsolWord] = parse_wiki_page(get_wiki_page())
