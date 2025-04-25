from translation import *
from dictionary import *

class FrenchToTsol():
    import spacy, spacy.cli, wn

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
            token_word = str(token)
            added = False
            prefix = ""
            suffix = ""
    
            # Ponctuation → inchangée
            if token.pos_ == "PUNCT":
                translated.append(token_word)
                continue
    
            # Traitement des pronoms
            if token.pos_ == "PRON":
                person = token.morph.get("Person")
                gender = token.morph.get("Gender")
                number = token.morph.get("Number")
                pron_type = token.morph.get("PronType")
    
                # Démonstratifs, relatifs, interrogatifs
                if pron_type and number:
                    if pron_type[0] == "Dem":
                        token_word = "æ" if number[0] == "Sing" else "лæпc"
                    elif pron_type[0] == "Rel":
                        token_word = "зat"
                    elif pron_type[0] == "Int":
                        token_word = {
                            "qui": "qσиaзag",
                            "quoi": "qσиoð"
                        }.get(token_word, "qσиoð")
    
                # Personnels (je, tu, il, nous...)
                if person and number:
                    table = {
                        ("1", "Sing"): "иŋ",
                        ("2", "Sing"): "tŋ",
                        ("3", "Sing"): "ϡŋ",
                        ("1", "Plur"): "иæß",
                        ("2", "Plur"): "tæß",
                        ("3", "Plur"): "ϡæß"
                    }
                    token_word = table.get((person[0], number[0]), token_word)
    
                if gender and gender[0] == "Fem":
                    prefix += "ẽ'"
    
                translated.append(prefix + token_word + suffix)
                continue
    
            # Mots spécifiques
            if token_word == "faite": token_word = "fait"
            elif token_word == "ça": token_word = "ce"

            if token_word == "son" and token.pos_ != "NOUN": token_word = "ses"
            if token_word == "sa": token_word = "ses"
    
            # Mise au singulier des noms et noms propres
            if token.pos_ in ["NOUN", "PROPN"]:
                number = token.morph.get("Number")
                if number and number[0] == "Plur":
                    token_word = token.lemma_
    
            # Lemmatisation des verbes
            if token.pos_ in ["VERB", "AUX"]:
                tense = token.morph.get("Tense")
                if "Fut" in tense:     prefix += "биc'"
                elif "Past" in tense or "Imp" in tense: prefix += "пac'"
                token_word = token.lemma_
    
            # Recherche dans le dictionnaire
            def_found = None
            for tsol_word in DICTIONARY:
                for definition in tsol_word.definitions:
                    if token_word.lower() in definition["trad"]:
                        def_found = definition
                        translated.append(prefix + tsol_word.word + suffix)
                        added = True
                        break
                if added:
                    break
    
            # Synonymes via WordNet si non trouvé
            if not added:
                synsets = self.fr_wn.synsets(token_word)
                synonyms = {lemma.lower() for syn in synsets for lemma in syn.lemmas()}
                for synonym in synonyms:
                    for tsol_word in DICTIONARY:
                        for definition in tsol_word.definitions:
                            if synonym in definition["trad"]:
                                translated.append(prefix + tsol_word.word + suffix)
                                added = True
                                break
                        if added:
                            break
                    if added:
                        break
    
            # Si toujours rien trouvé, encapsuler
            if not added:
                translated.append(f"{prefix}({token}){suffix}")
    
        # Mise en forme finale (majuscule + ponctuation propre)
        sentences = " ".join(translated).replace(" .", ".").replace(" ,", ",").replace(" ;", ";").split(".")
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                sentence = sentence.strip()
                sentences[i] = sentence[0].upper() + sentence[1:] + "."
    
        return "".join(sentences)

class TsolToFrench():
    def __init__(self):
        pass
    
    def translate(self, text: str, version:int=2):
        text_lower = text.lower()
        words_used:list[TsolWord] = []

        for word in DICTIONARY:
            if word.word.lower() in text_lower and not word in words_used:
                words_used.append(word)

        if version == 1:
            prompt = "You must translate from Tsol (Tsolenian, Tsolènire in French) to French. Tsol is an interpretive language; it does not have a valid grammar, but rather a standard grammar. The speaker is responsible for making themselves understood through the words and concepts available in the language. You will have this portion of the dictionary:\n"
            for word_used in words_used:
                prompt += str(word_used) + " | "
            prompt += "You will have this text to translate: \"" + text + "\" keeping the punctuation, capitalization, and everything else intelligently. Send only the translated text in your message. It's a work of interpretation, you need to find out what the speaker wanted to say with this minimalist language."
        elif version == 2:
            prompt = "Translate Tsol (Tsolenian; interpretive lang.) to French. Infer speaker intent. Dictionary:\n"
            for word_used in words_used:
                prompt += str(word_used) + " | "
            prompt += f"Translate: \"{text}\" Preserve punctuation & caps. Output only the translation."

        return prompt
