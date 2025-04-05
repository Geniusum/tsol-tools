from dictionary import *
import spacy, spacy.cli, os, wn

class FrenchToTsol():
    wn.download('omw-fr')
    fr_wn = wn.Wordnet('omw-fr')

    model = "fr_core_news_sm"
    try:
        nlp = spacy.load(model)
    except:
        print(f"Installing spacy model : {model}")
        spacy.cli.download(model)
        nlp = spacy.load(model)

    def __init__(self):
        pass
    
    def translate(self, text: str):
        doc = self.nlp(text)
        translated: list[str] = []

        for token in doc:
            added = False
            token_word = str(token)

            if token.pos_ == "PUNCT":
                translated.append(token_word)
                continue

            prefix = ""
            suffix = ""

            if token.pos_ == "PRON":                    
                person = token.morph.get("Person")
                gender = token.morph.get("Gender")
                number = token.morph.get("Number")
                pron_type = token.morph.get("PronType")

                if pron_type and number:
                    if pron_type[0] == "Dem" and number[0] == "Sing": token_word = "æ"
                    elif pron_type[0] == "Dem" and number[0] == "Plur": token_word = "лæпc"

                    if pron_type[0] == "Rel": token_word = "зat"

                    if pron_type[0] == "Int" and token_word == "qui": token_word = "qσиaзag"
                    elif pron_type[0] == "Int" and token_word == "quoi": token_word = "qσиoð"
                    elif pron_type[0] == "Int": token_word = "qσиoð"

                if person and number:
                    if person[0] == "1" and number[0] == "Sing": token_word = "иŋ"
                    elif person[0] == "2" and number[0] == "Sing": token_word = "tŋ"
                    elif person[0] == "3" and number[0] == "Sing": token_word = "ϡŋ"
                    elif person[0] == "1" and number[0] == "Plur": token_word = "иæß"
                    elif person[0] == "2" and number[0] == "Plur": token_word = "tæß"
                    elif person[0] == "3" and number[0] == "Plur": token_word = "ϡæß"

                if gender and gender[0] == "Fem":
                    prefix += "ẽ'"
                translated.append(prefix + token_word + suffix)
                continue

            if token.pos_ in ["VERB", "AUX"]:
                tense = token.morph.get("Tense")
                if tense == "Fut":
                    prefix += "биc'"
                elif tense in ["Past", "Imp"]:
                    prefix += "пac'"
                token_word = token.lemma_
            
            if token_word == "faite": token_word = "fait"
            elif token_word == "ça": token_word = "ce"

            def_founded = None
            for tsol_word in DICTIONNARY:
                for definition in tsol_word.definitions:
                    if token_word.lower() in definition["trad"]:
                        def_founded = definition
                        translated.append(prefix + tsol_word.word + suffix)
                        added = True
                        break
                if added:
                    break

            if def_founded is None and not added:
                synsets = self.fr_wn.synsets(token_word)
                synonyms = set()

                for syn in synsets:
                    for lemma in syn.lemmas():
                        synonyms.add(lemma.lower())

                for synonym in synonyms:
                    for tsol_word in DICTIONNARY:
                        for definition in tsol_word.definitions:
                            if synonym in definition["trad"]:
                                translated.append(prefix + tsol_word.word + suffix)
                                added = True
                                break
                        if added:
                            break
                    if added:
                        break

            if not added:
                translated.append(f"{prefix}({token}){suffix}")

        sentences = " ".join(translated).replace(" .", ".").replace(" ,", ",").replace(" ;", ";").split(".")

        for sentence_index, sentence in enumerate(sentences):
            if len(sentence): sentences[sentence_index] = sentence[0].upper() + sentence[1:] + "."

        return "".join(sentences)
