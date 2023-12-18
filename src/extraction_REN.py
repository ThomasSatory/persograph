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
    tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
    model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    ner_results = nlp(text)
    return (ner_results)

#prendre les resultats et les formater au format json pour les sauvegarder sous forme de liste d'objet json
#{
#   "id" : 1, 
#   "name" : "John Doe",
#   "category" : "PER",
#   "alias" : ["John","Doe","Johnny"]   
# }
def format_ner_results(data):
    concatenated_data = []
    #print (data)
    for i in data:
        if i['entity_group'] == 'PER' and i['score'] > 0.9 and i['word'] not in concatenated_data and len(i['word'])>2:
            concatenated_data.append(i['word'])
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
            if ((jaro_winkler_metric(name1, name2) >= 0.8 or (name1 in name2 or name2 in name1))
                and name1 != name2
                and result2['id'] != result['id']
                and (not name1.startswith('dr') or not name2.startswith('dr')) 
                and len(name1)>2 and len(name2)>2 
                and (not name1.endswith('cinq') or not name2.endswith('trois'))
                and (not name1.endswith('trois') or not name2.endswith('cinq'))
                ):
                result['alias'].append(result2['id'])
    data = delete_duplicates(data)
    show_result(data)
    return(data)

def is_shorter_named_entity(entity):
    entity_name_length = len(entity['name'])
    alias_lengths = [len(name) for name in entity['alias']]
    if not alias_lengths:
        return False
    if entity_name_length == max(alias_lengths):
        return True
    return entity_name_length < max(alias_lengths)

#on parcourt la liste des entités et on prend l'entitée nommée la plus grande 
#et on supprime les alias associés et à la place de sauvegarder des id non 
#sauvegarde les noms
def delete_duplicates(entities):
    data_cleaned = []

    #Parcourir la liste des entités pour mettre le nom des entitées à la place de leur id
    for entity in entities:
        if len(entity['alias']) > 0:
            string_aliases = []
            for alias_id in entity['alias']:
                alias_name = entities[alias_id]['name']
                string_aliases.append(alias_name)
            entity['alias'] = string_aliases

    entities = [entity for entity in entities if not is_shorter_named_entity(entity)]
    return (entities)

#méthode affichant les résultats avec pour chaque mot la liste de mot alias associés
def show_result(data):
    for result in data:
        print(result['name'])
        if (len(result['alias']) > 0):
            print(result['alias'])


def split_text_by_tokens(text, token_limit=500):
    # Séparation du texte en tokens (mots)
    tokens = text.split(' ')
    
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

        ner_results = []
        #découper text en blocs de 500 mots
        chunks = split_text_by_tokens(text, 500)
        for i, chunk in enumerate(chunks, start=1):
            ner_results += (extract_REN(chunk))
        #print (ner_results)
        formatted_ner_results = format_ner_results(ner_results)
        #print(formatted_ner_results)

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

        ner_results = []
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
