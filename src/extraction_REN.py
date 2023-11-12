import os
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import json

path_caverne_normalized = "../res/corpus_asimov_leaderboard_normalized/les_cavernes_d_acier_normalized"
path_prelude_normalized = "../res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized"

path_caverne_REN = "../res/corpus_asimov_leaderboard_REN/les_cavernes_d_acier_REN"
path_prelude_REN = "../res/corpus_asimov_leaderboard_REN/prelude_a_fondation_REN"

def extract_REN(text):
    tokenizer = AutoTokenizer.from_pretrained("Davlan/distilbert-base-multilingual-cased-ner-hrl")
    model = AutoModelForTokenClassification.from_pretrained("Davlan/distilbert-base-multilingual-cased-ner-hrl")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    ner_results = nlp(text)
    print(ner_results)
    #si le mot commence par ## on prend le mot précédent et on le concatène avec le mot actuel
    concatenated_data = []
    for result in ner_results:
        if result['entity'] == 'B-PER' or result['entity'] == 'I-PER':
            for result2 in ner_results:
                if result2['entity'] == 'B-PER' or result2['entity'] == 'I-PER':
                    # si end est dans la fourchette entre start et start + 2
                    if result['end'] == result2['start'] and result['word'] != result2['word']:
                        result['word'] = result['word'] + result2['word'][2:]
                        result['end'] = result2['end']
                        result['entity'] = 'PER'
                        result2['entity'] = 'O'
                    elif result['end'] >= result2['start'] and result['end'] <= result2['start'] + 2:
                        result['word'] = result['word'] + result2['word'][2:]
                        result['end'] = result2['end']
                        result['entity'] = 'PER'
                        result2['entity'] = 'O'
            if (result['word'] not in concatenated_data and result['word'][0] != '#' and (result['entity'] == 'PER' or result['entity'] == 'B-PER' or result['entity'] == 'I-PER')):
                concatenated_data.append(result['word'])
    print(concatenated_data)
    return(concatenated_data)

#prendre les resultats et les formater au format json pour les sauvegarder sous forme de liste d'objet json
#{
#   "id" : 1, 
#   "name" : "John Doe",
#   "category" : "PER",
#   "alias" : [1,2,6]   
# }
def format_ner_results(data):
    formatted_ner_results = []
    id = 0
    for word in data:
        formatted_ner_results.append({
            "id": id,
            "name": word,
            "category": 'PER',
            "alias": []
        })
        id += 1
    print(formatted_ner_results)
    return(formatted_ner_results)

def main():
    # Boucle sur tous les fichiers du corpus_pdf_directory en lisant chaque fichier 300 caracteres par 300 caracteres
    for file in os.listdir(path_caverne_normalized):
        file_path = os.path.join(path_caverne_normalized, file)  # Chemin complet du fichier
        output_file = file.replace("normalized.txt", "REN.json")  # Nom du fichier de sortie

        try:
            # Ouvrir le fichier en lecture avec l'encodage utf-8 et lire seulement 300 caracteres par 300 caracteres
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
            return

        #normaliser le texte
        ner_results = extract_REN(text)
        formatted_ner_results = format_ner_results(ner_results)

        #save les resultats dans un fichier txt dans le dossier res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized
        with open(os.path.join(path_caverne_REN, output_file), "w", encoding="utf-8") as f:
            json.dump(formatted_ner_results, f, ensure_ascii=False, indent=4)

        print(f"Traitement terminé pour {file_path}.")

if __name__ == "__main__":
    main()
