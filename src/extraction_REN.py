import os
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import json
from fuzzywuzzy import fuzz
from jaro import jaro_winkler_metric

path_caverne_normalized = "../res/corpus_asimov_leaderboard/les_cavernes_d_acier"
path_prelude_normalized = "../res/corpus_asimov_leaderboard/prelude_a_fondation"

path_caverne_REN = "../res/corpus_asimov_leaderboard_REN/les_cavernes_d_acier_REN"
path_prelude_REN = "../res/corpus_asimov_leaderboard_REN/prelude_a_fondation_REN"
path_dictionnary = "../res/dictionnary.json"

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
            if (is_similar(name1, name2)):
                result['alias'].append(result2['id'])
    data = delete_duplicates(data)
    show_result(data)
    return(data)


def is_similar(name1, name2):
    name1 = name1.lower()
    name2 = name2.lower()

    if (name1.startswith('maître') and name2.startswith('maître')):
        name1 = name1.split('maître', 1)[-1]
        name2 = name2.split('mâitre', 1)[-1]
    
    if (len(name2.split(' ')) > 1 and len(name1.split(' ')) > 1):
        if (name1.endswith('seldon') and name2.endswith('seldon')):
            name1 = name1.split(' ')[0]
            name2 = name2.split(' ')[0]
        elif (name1.endswith('randa') and name2.endswith('randa')):
            name1 = name1.split(' ')[0]
            name2 = name2.split(' ')[0]
    if (((jaro_winkler_metric(name1, name2) >= 0.8 or fuzz.ratio(name1, name2) >= 80)
         or (name1 in name2 or name2 in name1)
         or (name1.startswith('cléon') and name2.endswith('empereur'))
         or ((len(name1.split(' ')) > 1 and len(name2.split(' ')) > 1 and (name1.split(' ')[1] in name2 or name2.split(' ')[1] in name1))))
                and name1 != name2
                and (not name1.startswith('dr') or not name2.startswith('dr')) 
                and len(name1)>2 and len(name2)>2 
                and (not name1.endswith('cinq') or not name2.endswith('trois'))
                and (not name1.endswith('trois') or not name2.endswith('cinq'))
                and (not name1.endswith('elisabeth') or not name2.endswith('elijah'))
                and (not name1.endswith('dors seldon') or not name2.endswith('seldon'))
                ):
        return True
    return False


def pretraitement(name1,name2):
    list_maitre = ['maître-du-soleil','maîtresse','maître','maître-du-','maître-']

    if ((name1 == 'goutte-de-pluie' and name2 == 'goutte-de-pluie')
        or (name1 == 'baley' and name2 == 'baley')
        or (name1 == 'seldon' and name2 == 'seldon')
        or (name1 == 'dors' and name2 == 'dors')
        or (name1 == 'randa' and name2 == 'randa')
        or (name1 == 'marbie' and name2 == 'maître') or (name1 == 'maître' and name2 == 'marbie')
        or (name1 == 'marron' and name2 == 'marlo tanto') or (name1 == 'marlo tanto' and name2 == 'marron') 
        or (name1 == 'dors venabili' and name2 == 'dors seldon') or (name1 == 'dors seldon' and name2 == 'dors venabili')
        or (name1 == 'kan' and name2 == 'kiangtow randa') or (name1 == 'kiangtow randa' and name2 == 'kan')
        or (name1 == 'barrett' and name2 == 'vince barrett') or (name1 == 'vince barrett' and name2 == 'barrett')
        or (name1 == 'chetter hummin' and name2 == 'chester') or (name1 == 'chester' and name2 == 'chetter hummin')
        or (name1 == 'amaryl' and name2 == 'yugo amaryl')
        or (name1 == 'hummin' and name2 == 'chetter hummin')
        or (name1 == 'demerzel' and name2 == 'eto demerzel')
        or (name1 == 'marbie' and name2 == 'maître seldon')):
        return False
    
    if ((name1.endswith('venabili') and name2.endswith('machinchose'))
        or (name1.endswith('hari seldon') and name2.endswith('maître'))
        or (name1.endswith('hari seldon') and name2.endswith('maître seldon'))):
        return True

    if (len(name1.split(' ')) > 1):
        if (name1.split(' ')[0] in list_maitre):
            name1 = name1.split(' ')[1]

        if (name1.endswith('cinq') or name1.endswith('trois')):
            name2 = name2.rpartition('-')[-1] if '-' in name2 else name2
        
        if (name1.endswith('baley') or name1.endswith('randa') or name1.endswith('seldon')  or name1.endswith('iv')):
            name1 = name1.split(' ')[0]

    if (len(name2.split(' ')) > 1):
        if (name2.endswith('cinq') or name1.endswith('trois')):
            name2 = name2.rpartition('-')[-1] if '-' in name2 else name2

        if (name2.endswith('baley') or name2.endswith('randa') or name2.endswith('seldon')):
            name2 = name2.split(' ')[0]

        #si le premier mot est robot alors on supprime robot dans la chaine 
        if (name2.split(' ')[0] == 'robot'):
            name2 = name2.split(' ', 1)[-1]

    if (name1 == name2):
        return True
    
    if (name1.startswith('dr') and name2.startswith('hano') or name1.startswith('hano') and name2.startswith('dr')):
        return False

    if (name1.startswith('elisabeth') or name2.startswith('elisabeth')):
        return False

    return is_similar(name1,name2)

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

#fonction pour ajouter les nouvelles entités nommées au dictionnaire
#si une entitée de data est déjà dans le dictionnaire on ne l'ajoute pas
#sinon on l'ajoute
#si une entité de data est déjà en temps qu'alias dans le dictionnaire on ne l'ajoute pa
#mais on ajoute ses alias à l'entité déjà présente dans le dictionnaire
#le chemin du fichier est path_dictionnary
def add_to_dictionnary(data):
    if not os.path.exists(path_dictionnary) or os.path.getsize(path_dictionnary) == 0:
        # Si le fichier n'existe pas ou est vide, initialisez une liste vide
        dictionary = []
    else:
        try:
            with open(path_dictionnary, "r", encoding="utf-8") as f:
                dictionary = json.load(f)
        except json.JSONDecodeError:
            # Gérer l'erreur si le fichier contient des données JSON invalides
            print("Le fichier JSON est invalide ou vide.")
            dictionary = []

    alias_set = set()
    for entry in dictionary:
        alias_set.update(entry['alias'])

    for new_entity in data:
        new_name = new_entity['name'].lower()
        new_aliases = set(alias.lower() for alias in new_entity['alias'])

        # Cas 1: Nouvelle entité a le même nom qu'une entité du dictionnaire
        found = False
        for entry in dictionary:
            if new_name == entry['name']:
                entry['alias'] = list(set(entry['alias']) | new_aliases)
                found = True
                #print new_name en jaune
                print ('\033[93m' + new_name + '\033[0m' + ' existe déjà et on a merge les alias')
                break

        # Cas 2: Nouvelle entité est dans une liste d'alias d'une entité du dictionnaire
        if not found:
            for entry in dictionary:
                if new_name in entry['alias']:
                    entry['alias'] = list(set(entry['alias']) | new_aliases)
                    found = True
                    #print new_name en rouge
                    print ('\033[91m' + new_name + '\033[0m' + ' est un alias de ' + entry['name'] + ' et on a merge les alias')
                    break

        # Cas 3: Nouvelle entité a un alias correspondant à une entité existante ou à ses alias
        if not found:
            for entry in dictionary:
                for alias in entry['alias']:
                    for new_alias in new_aliases:
                        if pretraitement(alias, new_alias):
                            print (alias + ' est un alias de ' + new_alias + ' et on a merge les alias')
                            entry['alias'] = list(set(entry['alias']) | new_aliases | {new_name})
                            found = True
                            #print new_name en orange
                            print ('\033[33m' + new_name + '\033[0m' + ' est un alias de ' + entry['name'] + ' et on a merge les alias')
                            break
                if found:
                    break

        # Cas 4: Si la nouvelle entité n'a pas été fusionnée, l'ajouter simplement au dictionnaire
        if not found:
            dictionary.append({'id': len(dictionary), 'name': new_name, 'alias': list(new_aliases)})
            #print new_name en vert
            print ('\033[32m' + new_name + '\033[0m' + ' a été ajouté au dictionnaire')

    with open(path_dictionnary, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)

def clean_dictionary(dictionary):
    to_delete = []

    for entry in dictionary:
        for entry2 in dictionary:
            if pretraitement(entry['name'], entry2['name']) and entry['id'] != entry2['id']  and entry2 not in to_delete and entry not in to_delete:
                #merge les alias et ajouter entry{name} si il n'est pas déjà dans la liste des alias
                entry['alias'] = list(set(entry['alias']) | set(entry2['alias']))
                if entry2['name'] not in entry['alias']:
                    entry['alias'].append(entry2['name'])
                print('On supprime ' + entry2['name'] + ' et on ajoute ses alias à ' + entry['name'])
                to_delete.append(entry2)
                break
  
    # Supprimer les entrées qui ont été fusionnées
    for entry in to_delete:
        dictionary.remove(entry)

    with open(path_dictionnary, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)

def main():
    ren = False
    if (ren):
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

            add_to_dictionnary(formatted_ner_results)

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
            formatted_ner_results = format_ner_results(ner_results)

            #save les resultats dans un fichier txt dans le dossier res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized
            with open(os.path.join(path_prelude_REN, output_file), "w", encoding="utf-8") as f:
                json.dump(formatted_ner_results, f, ensure_ascii=False, indent=4)

            add_to_dictionnary(formatted_ner_results)

            print(f"Traitement terminé pour {file_path}.")
        
        # Nettoyage du dictionnaire
        #with open(path_dictionnary, "r", encoding="utf-8") as f:
        #   dictionary = json.load(f)
        #cleaned_dict = clean_dictionary(dictionary)
        #with open(path_dictionnary, "w", encoding="utf-8") as f:
            #json.dump(cleaned_dict, f, ensure_ascii=False, indent=4)
    else:

        #supprimer le contenu du document dictionnaire
        with open(path_dictionnary, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        
        for file in os.listdir(path_caverne_REN):
            file_path = os.path.join(path_caverne_REN, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
                return
        
            ner_results = json.loads(text)
            add_to_dictionnary(ner_results)
            print(f"Traitement terminé pour {file_path}.")
        
        for file in os.listdir(path_prelude_REN):
            file_path = os.path.join(path_prelude_REN, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
                return
        
            ner_results = json.loads(text)
            add_to_dictionnary(ner_results)
            print(f"Traitement terminé pour {file_path}.")
        
        # Nettoyage du dictionnaire
        for i in range(10):
            with open(path_dictionnary, "r", encoding="utf-8") as f:
                dictionary = json.load(f)
            clean_dictionary(dictionary)


if __name__ == "__main__":
    main()
