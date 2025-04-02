import torch
from transformers import pipeline
import dictionary  # Module dictionnary.py contenant le dictionnaire Tsolènire
import re

# Détection de la langue
def detect_language(text):
    """Détecte si le texte est en Tsolènire ou une autre langue."""
    tsol_alphabet = "AÆÐOÖTŦEẼПФЗΣGḠИẞБCRWŴϠKḲQMNØЛЧŊŒaæðoötŧeẽпфзσgḡиßбcrwŵϡkḳqmnøлчŋœ"
    return all(char in tsol_alphabet or char.isspace() or char in ",.!?" for char in text)

# Charger le modèle
pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", 
                torch_dtype=torch.bfloat16, device_map="auto")

# Charger le dictionnaire Tsolènire-Français
tsol_words = dictionary.parse_wiki_page(dictionary.get_wiki_page())

def translate_to_tsol(text):
    """Traduit une phrase d'une langue vers le Tsolènire en utilisant le dictionnaire."""
    words = text.lower().split()
    translated_words = []
    for word in words:
        matches = [w for w in tsol_words if word in sum([d['trad'] for d in w.definitions], [])]
        if matches:
            translated_words.append(matches[0].word)
        else:
            translated_words.append(word)  # Mot inconnu, on le garde
    return " ".join(translated_words)

def translate_from_tsol(text):
    """Traduit une phrase du Tsolènire vers le Français en utilisant le dictionnaire."""
    words = text.lower().split()
    translated_words = []
    for word in words:
        match = next((w for w in tsol_words if w.word == word), None)
        if match:
            translated_words.append(match.default['trad'][0])
        else:
            translated_words.append(word)  # Mot inconnu, on le garde
    return " ".join(translated_words)

def generate_with_dictionary(input_text, translated_text):
    """Génère un texte en utilisant le dictionnaire pour fournir des exemples au modèle."""
    # Préparer le dictionnaire complet pour TinyLlama (ajouter plus de mots)
    dictionary_examples = ""
    for word in translated_text.split():
        match = next((w for w in tsol_words if w.word == word), None)
        if match:
            dictionary_examples += f"{match.word} ({', '.join(match.default['trad'])})\n"

    # Ajouter plus d'exemples du dictionnaire (par exemple, les 10 premiers mots)
    dictionary_examples_full = ""
    for word in tsol_words:  # Ajouter les 10 premiers mots pour plus de contexte
        dictionary_examples_full += f"{word.word} : {', '.join(word.default['trad'])}\n"

    # Créer un prompt plus clair et plus explicite
    prompt = f"Le Tsolènire est une langue fictive utilisant un alphabet unique : AÆÐOÖTŦEẼПФЗΣGḠИẞБCRWŴϠKḲQMNØЛЧŊŒ.\n"
    prompt += f"Voici des exemples de mots Tsolènire et leurs traductions :\n{dictionary_examples_full}\n\n"
    prompt += f"Traduisez la phrase suivante en Tsolènire : {input_text}"

    # Générer une réponse avec le modèle
    messages = [
        {"role": "system", "content": "Vous êtes un traducteur intelligent pour la langue Tsolènire."},
        {"role": "user", "content": prompt}
    ]
    
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    max_tokens = min(2 * len(translated_text.split()), 1000)  # Limite proportionnelle à la longueur
    outputs = pipe(prompt, max_new_tokens=max_tokens, do_sample=True, temperature=0.7)

    return outputs[0]["generated_text"]

print("Bienvenue dans le traducteur Tsolènire. Tapez 'exit' pour quitter.")
while True:
    user_input = input("Entrez une phrase : ").strip()
    if user_input.lower() == "exit":
        break
    
    if detect_language(user_input):
        print("→ Traduction (Tsolènire → Français) :", translate_from_tsol(user_input))
    else:
        translated = translate_to_tsol(user_input)
        print("→ Traduction (Français → Tsolènire) :", translated)

        # Générer une correction grammaticale avec TinyLlama
        corrected_translation = generate_with_dictionary(user_input, translated)
        print("→ Version corrigée par le modèle :", corrected_translation)
