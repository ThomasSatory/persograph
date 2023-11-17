import os
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import json
from Levenshtein import distance
from jaro import jaro_winkler_metric

path_caverne_normalized = "../res/corpus_asimov_leaderboard/les_cavernes_d_acier"
path_prelude_normalized = "../res/corpus_asimov_leaderboard/prelude_a_fondation"

path_caverne_REN = "../res/corpus_asimov_leaderboard_REN/les_cavernes_d_acier_REN"
path_prelude_REN = "../res/corpus_asimov_leaderboard_REN/prelude_a_fondation_REN"

def extract_REN(text):
    tokenizer = AutoTokenizer.from_pretrained("Davlan/distilbert-base-multilingual-cased-ner-hrl")
    model = AutoModelForTokenClassification.from_pretrained("Davlan/distilbert-base-multilingual-cased-ner-hrl")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    ner_results = nlp(text)
    return (ner_results)

#prendre les resultats et les formater au format json pour les sauvegarder sous forme de liste d'objet json
#{
#   "id" : 1, 
#   "name" : "John Doe",
#   "category" : "PER",
#   "alias" : ["John","Doe","Johnny"]   
# }
def format_ner_results(ner_results):
    concatenated_data = []
    for result in ner_results:
        if result['entity'] == 'B-PER' or result['entity'] == 'I-PER':
            for result2 in ner_results:
                if result2['entity'] == 'I-PER':
                    if result['end'] == result2['start'] and result['word'] != result2['word'] and result2['entity'] == 'I-PER' and result['index']+1  == result2['index'] and result['index']+1  == result2['index']:
                        if ('##' in result2['word'] and len(result2['word'].split()) < 2):
                            result['word'] = result['word'] + result2['word'][2:]
                        elif (len(result2['word'].split()) < 2):
                            result['word'] = result['word'] + result2['word']
                        result['end'] = result2['end']
                        result['index'] = result2['index']
                        result['entity'] = 'PER'
                        result2['entity'] = 'O'
                        # si start est dans la fourchette end et end +2
                    elif (result['end'] < result2['start'] and result['end']  >= result2['start'] - 1 and result['word'] != result2['word'] and result2['entity'] == 'I-PER' and result['index']+1  == result2['index']):
                        #si le mot fait plus de 2 mots on ajoute pas le mot
                        if ('##' in result2['word'] and len(result2['word'].split()) < 2):
                            result['word'] = result['word'] + result2['word'][2:]
                        elif (len(result2['word'].split()) < 2):
                            result['word'] = result['word'] + " " + result2['word']
                        result['end'] = result2['end']
                        result['index'] = result2['index']
                        result['entity'] = 'PER'
                        result2['entity'] = 'O'
            if (result['word'] not in concatenated_data and result['word'][0] != '#' 
                and (result['entity'] == 'PER' or result['entity'] == 'B-PER' 
                or result['entity'] == 'I-PER') and len(result['word']) >= 2 and len (result['word'].split()) < 3):
                concatenated_data.append(result['word'])
    formatted_ner_results = []
    id = 0
    for word in concatenated_data:
        formatted_ner_results.append({
            "id": id,
            "name": word,
            "category": 'PER',
            "alias": []
        })
        id += 1
    return(alias_creation(formatted_ner_results))

#méthode prenant en paramètre les données extraites et créant les alias pour chaque entité
def alias_creation(data):
    for result in data:
        for result2 in data:
            name1 = result['name'].lower()
            name2 = result2['name'].lower()
            if (jaro_winkler_metric(name1, name2) >= 0.8 and name1 != name2):
                result['alias'].append(result2['id'])
            #si le mot contient un bigramme ou un trigramme du mot actuel
            elif (name1 in name2 and name1 != name2):
                result['alias'].append(result2['id'])
    return(data)


def split_text_by_tokens(text, token_limit=500):
    # Séparation du texte en tokens (mots)
    tokens = re.findall(r'\b\w+\b', text)
    
    # Initialisation des sous-textes
    token_chunks = []
    current_chunk = []

    # Parcours des tokens pour former les sous-textes
    for token in tokens:
        current_chunk.append(token)
        # Vérification de la limite de tokens par sous-texte
        if len(current_chunk) >= token_limit:
            token_chunks.append(' '.join(current_chunk))
            current_chunk = []

    # Si des tokens restent à la fin, les ajouter à un dernier sous-texte
    if current_chunk:
        token_chunks.append(' '.join(current_chunk))

    return token_chunks


def main():
    # Boucle sur tous les fichiers du corpus_pdf_directory en lisant chaque fichier 300 caracteres par 300 caracteres
    for file in os.listdir(path_caverne_normalized):
        file_path = os.path.join(path_caverne_normalized, file)  # Chemin complet du fichier
        output_file = file.replace(".txt.preprocessed", "_REN.json")  # Nom du fichier de sortie

        try:
            # Ouvrir le fichier en lecture avec l'encodage utf-8 et lire seulement 300 caracteres par 300 caracteres
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
            return

        #découper text en blocs de 500 mots
        ner_results = []
        chunks = split_text_by_tokens(text, 500)
        for i, chunk in enumerate(chunks, start=1):
            ner_results += (extract_REN(chunk))
        print (ner_results)
        formatted_ner_results = format_ner_results(ner_results)
        print(formatted_ner_results)

        #save les resultats dans un fichier txt dans le dossier res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized
        with open(os.path.join(path_caverne_REN, output_file), "w", encoding="utf-8") as f:
            json.dump(formatted_ner_results, f, ensure_ascii=False, indent=4)

        print(f"Traitement terminé pour {file_path}.")

    
    # Boucle sur tous les fichiers du corpus_pdf_directory en lisant chaque fichier 300 caracteres par 300 caracteres
    for file in os.listdir(path_prelude_normalized):
        file_path = os.path.join(path_prelude_normalized, file)  # Chemin complet du fichier
        output_file = file.replace(".txt.preprocessed", "_REN.json")  # Nom du fichier de sortie

        try:
            # Ouvrir le fichier en lecture avec l'encodage utf-8 et lire seulement 300 caracteres par 300 caracteres
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
            return

        #découper text en blocs de 500 mots
        chunks = split_text_by_tokens(text, 500)
        for i, chunk in enumerate(chunks, start=1):
            ner_results += (extract_REN(chunk))
        print (ner_results)
        formatted_ner_results = format_ner_results(ner_results)
        print(formatted_ner_results)

        #save les resultats dans un fichier txt dans le dossier res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized
        with open(os.path.join(path_prelude_REN, output_file), "w", encoding="utf-8") as f:
            json.dump(formatted_ner_results, f, ensure_ascii=False, indent=4)

        print(f"Traitement terminé pour {file_path}.")

if __name__ == "__main__":
    main()
