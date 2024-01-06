import os
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import json
from fuzzywuzzy import fuzz
from jaro import jaro_winkler_metric

path_caverne_normalized = "res/corpus_asimov_leaderboard/les_cavernes_d_acier"
path_prelude_normalized = "res/corpus_asimov_leaderboard/prelude_a_fondation"

path_caverne_REN = "res/corpus_asimov_leaderboard_REN/les_cavernes_d_acier_REN"
path_prelude_REN = "res/corpus_asimov_leaderboard_REN/prelude_a_fondation_REN"
path_dictionnary = "res/dictionnary.json"

def extract_REN(nlp,text: str) -> list:
    """

        Méthode qui prend en paramètre un NER et un texte et qui renvoie les données extraites

        # Arguments
        * nlp: Le NER utilisé pour renconnaitre les entités nommées
        * text: texte à analyser
    """
    ner_results = nlp(text)
    return (ner_results)

def format_ner_results(data: list) -> list:
    """

        Méthode qui prend en paramètre les données extraites et qui les formate au format json
        en fitrant sur une liste de fausses entités nommées

        Par exemple :
            {
                "id" : 1,
                "name" : "John Doe",
                "category" : "PER",
                "alias" : ["John","Doe","Johnny"]
            }

        # Arguments
        * data: données extraites
    """

    concatenated_data = []

    fausses_entites = ['chester','heisenberg','frère','streeling','mycogène','mycogénien',
                       'dahl','anat bigell','ba-lee','exos','trantor','galactos','hélicon',
                       'héliconien','shakespeare','churchill','spacien','marron']
    for i in data:
        if i['entity_group'] == 'PER' and i['score'] > 0.9 and i['word'] not in concatenated_data and len(i['word'])>2 and i['word'].lower() not in fausses_entites:
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


def alias_creation(chapitre: list) -> list:

    """
        Méthode qui prend en paramètre les données extraites et créant les alias pour chaque entité

        # Arguments
        * chapitre: liste des entités nommées d'un chapitre
    """

    for result in chapitre:
        for result2 in chapitre:
            name1 = result['name']
            name2 = result2['name']
            if (is_similar(name1, name2)):
                result['alias'].append(result2['id'])
    chapitre = delete_duplicates(chapitre)
    show_result(chapitre)
    return(chapitre)


def is_similar(name1: str, name2: str)  -> bool:
    """

        Méthode qui prend en paramètre deux chaines de caractères et qui renvoie True si elles sont similaires
        et False sinon en utilisant la méthode jaro winkler, le fuzzy matching et des règles

        # Arguments
        * name1: chaine de caractères
        * name2: chaine de caractères

    """

    name1 = name1.lower()
    name2 = name2.lower()

    list_maitre = ['maître-du-soleil','maîtresse','maître-du-','maître-','maître']

    if (len(name2.split(' ')) > 1 and len(name1.split(' ')) > 1):
        if (name1.endswith('seldon') and name2.endswith('seldon')):
            name1 = name1.split(' ')[0]
            name2 = name2.split(' ')[0]
        elif (name1.endswith('randa') and name2.endswith('randa')):
            name1 = name1.split(' ')[0]
            name2 = name2.split(' ')[0]

    if (len(name1.split(' ')) > 1):
        if (name1.split(' ')[0] in list_maitre):
            name1 = name1.split(' ', 1)[-1]
    
    if (len(name2.split(' ')) > 1):
        if (name2.split(' ')[0] in list_maitre):
            name2 = name2.split(' ', 1)[-1]
    if (name1.startswith('raych') and name2 == 'rachelle') or (name1 == 'rachelle' and name2.startswith('raych')):
        return False
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

def pretraitement_dictionnary(name1: str,name2:str) -> bool:
    """
        Méthode réservé à la création et au nettoyage du dictionnaire, qui prend en paramètre deux chaines de caractères et qui renvoie True si elles sont similaires
        et False sinon en prenant en compte certains cas particuliers qui sont gérés par des règles

        # Arguments
        * name1: chaine de caractères
        * name2: chaine de caractères
    """

    list_maitre = ['maître-du-soleil','maîtresse','maître','maître-du-','maître-']
    list_cleon = ['cléon ier','cléon','sire','empereur','l\'empereur']
    name1 = name1.lower()
    name2 = name2.lower()
    if ((name1 == 'goutte-de-pluie' and name2 == 'goutte-de-pluie')
        or (name1 == 'baley' and name2 == 'baley')
        or (name1 == 'seldon' and name2 == 'seldon')
        or (name1 == 'dors' and name2 == 'dors')
        or (name1 == 'randa' and name2 == 'randa')
        or (name1 == 'marbie' and name2 == 'maître') or (name1 == 'maître' and name2 == 'marbie')
        or (name1 == 'marron' and name2 == 'marlo tanto') or (name1 == 'marlo tanto' and name2 == 'marron') 
        or (name1 == 'dors venabili' and name2 == 'dors seldon') or (name1 == 'dors seldon' and name2 == 'dors venabili')
        or (name1 == 'dors venabili' and name2 == 'dors') or (name1 == 'dors' and name2 == 'dors venabili')
        or (name1 == 'kan' and name2 == 'kiangtow randa') or (name1 == 'kiangtow randa' and name2 == 'kan')
        or (name1 == 'chetter hummin' and name2 == 'chester') or (name1 == 'chester' and name2 == 'chetter hummin')
        or (name1 == 'amaryl' and name2 == 'yugo amaryl')
        or (name1 == 'hummin' and name2 == 'chetter hummin')
        or (name1 == 'demerzel' and name2 == 'eto demerzel')
        or (name1 == 'marbie' and name2 == 'maître seldon')
        or (name1 == 'raych' and name2 == 'rachelle') or (name1 == 'rachelle' and name2 == 'raych')
        or (name1 == 'raych seldon' and name2 == 'rachelle') or (name1 == 'rachelle' and name2 == 'raych seldon')
        or (name1 == 'bentley' and name2 == 'ben') or (name1 == 'ben' and name2 == 'bentley')
        or (name1 == 'bentley baley' and name2 == 'ben') or (name1 == 'ben' and name2 == 'bentley baley')):
        return False
    
    if ((name1.endswith('venabili') and name2.endswith('machinchose'))
        or (name1.endswith('hari seldon') and name2.endswith('maître'))
        or (name1.endswith('hari seldon') and name2.endswith('maître seldon'))
        or (name1.endswith('cléon') and name2.endswith('l\'empereur'))
        or (name1.endswith('barrett') and name2.endswith('barrett'))
        or (name1.endswith('tisalver') and name2.endswith('casilia'))
        or (name1.endswith('robot daneel olivaw') and name2.endswith('maître robot'))
        or (name1.endswith('sarton') and name2.endswith('sarton'))
        or (name1 in list_cleon and name2 in list_cleon)):
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
        if (name2.split(' ')[0] == 'robot'):
            name2 = name2.split(' ', 1)[-1]
    if (name1 == name2):
        return True
    
    if (name1.startswith('dr') and name2.startswith('hano') or name1.startswith('hano') and name2.startswith('dr')):
        return False
    if (name1.startswith('elisabeth') or name2.startswith('elisabeth')):
        return False
    return is_similar(name1,name2)



def pretraitement_chapter(name1: str,name2: str) -> bool:
    """
        Méthode réservé au nettoyage de chapitre, qui prend en paramètre deux chaines de caractères et qui renvoie True si elles sont similaires
        et False sinon en prenant en compte certains cas particuliers qui sont gérés par des règles

        # Arguments
        * name1: chaine de caractères
        * name2: chaine de caractères
    """

    list_maitre = ['maître-du-soleil','maîtresse','maître','maître-du-','maître-']
    list_cleon = ['cléon ier','cléon','sire','empereur','l\'empereur']
    name1 = name1.lower()
    name2 = name2.lower()

    if ((name1 == 'goutte-de-pluie' and name2 == 'goutte-de-pluie')
        or (name1 == 'baley' and name2 == 'baley')
        or (name1 == 'seldon' and name2 == 'seldon')
        or (name1 == 'dors' and name2 == 'dors')
        or (name1 == 'randa' and name2 == 'randa')
        or (name1 == 'marbie' and name2 == 'maître') or (name1 == 'maître' and name2 == 'marbie')
        or (name1 == 'marron' and name2 == 'marlo tanto') or (name1 == 'marlo tanto' and name2 == 'marron') 
        or (name1 == 'dors venabili' and name2 == 'dors seldon') or (name1 == 'dors seldon' and name2 == 'dors venabili')
        or (name1 == 'dors venabili' and name2 == 'dors') or (name1 == 'dors' and name2 == 'dors venabili')
        or (name1 == 'kan' and name2 == 'kiangtow randa') or (name1 == 'kiangtow randa' and name2 == 'kan')
        or (name1 == 'chetter hummin' and name2 == 'chester') or (name1 == 'chester' and name2 == 'chetter hummin')
        or (name1 == 'amaryl' and name2 == 'yugo amaryl')
        or (name1 == 'hummin' and name2 == 'chetter hummin')
        or (name1 == 'demerzel' and name2 == 'eto demerzel')
        or (name1 == 'marbie' and name2 == 'maître seldon')
        or (name1 == 'raych' and name2 == 'rachelle') or (name1 == 'rachelle' and name2 == 'raych')
        or (name1 == 'raych seldon' and name2 == 'rachelle') or (name1 == 'rachelle' and name2 == 'raych seldon')
        or (name1 == 'bentley' and name2 == 'ben') or (name1 == 'ben' and name2 == 'bentley')
        or (name1 == 'bentley baley' and name2 == 'ben') or (name1 == 'ben' and name2 == 'bentley baley')
        or (name1 == 'maître-du-soleil' and name2 == 'maître seldon') or (name1 == 'maître seldon' and name2 == 'maître-du-soleil')
        or (name1 == 'maîtresse' and name2 == 'maître seldon') or (name1 == 'maître seldon' and name2 == 'maîtresse')
        or (name1 == 'goutte-de-pluie quarante- cinq' and name2 == 'goutte-de-pluie') or (name1 == 'goutte-de-pluie' and name2 == 'goutte-de-pluie quarante- cinq')
        or (name1 == 'maître tisalver' and name2 == 'casilia tisalver') or (name1 == 'casilia tisalver' and name2 == 'maître tisalver')
        or (name1 == 'maîtresse tisalver' and name2 == 'sse tisalver') or (name1 == 'sse tisalver' and name2 == 'maîtresse tisalver')
        or (name1 == 'maître seldon' and name2 == 'seldon') or (name1 == 'seldon' and name2 == 'maître seldon')
        or (name1 == 'goutte- de-pluie quarante-trois' and name2.startswith('goutte-de-pluie')) or (name1.startswith('goutte-de-pluie') and name2 == 'goutte- de-pluie quarante-trois')
        or (name1 == 'goutte-de-pluie quarante- cinq' and name2 == 'goutte-de-pluie quarante- cinq') or (name1 == 'goutte-de-pluie quarante- cinq' and name2 == 'goutte-de-pluie quarante- cinq')):
        return False
    
    if ((name1.endswith('venabili') and name2.endswith('machinchose'))
        or (name1.endswith('hari seldon') and name2.endswith('maître'))
        or (name1.endswith('hari seldon') and name2.endswith('maître seldon'))
        or (name1.endswith('barrett') and name2.endswith('barrett'))
        or (name1.endswith('tisalver') and name2.endswith('casilia'))
        or (name1.endswith('robot daneel olivaw') and name2.endswith('maître robot'))
        or (name1.endswith('daneel') and name2.endswith('olivaw'))
        or (name1.endswith('sarton') and name2.endswith('sarton'))
        or (name1 in list_cleon and name2 in list_cleon)):
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

        if (name2.split(' ')[0] == 'robot'):
            name2 = name2.split(' ', 1)[-1]

    if (name1 == name2):
        return True
    
    if (name1.startswith('dr') and name2.startswith('hano') or name1.startswith('hano') and name2.startswith('dr')):
        return False

    if (name1.startswith('elisabeth') or name2.startswith('elisabeth')):
        return False

    return is_similar(name1,name2)

def is_shorter_named_entity(entity: dict) -> bool:
    """
        Vérifier si l'entité nommée est plus courte que ses alias

        # Arguments
        * entity: entité nommée
    """
    entity_name_length = len(entity['name'])
    alias_lengths = [len(name) for name in entity['alias']]
    if not alias_lengths:
        return False
    if entity_name_length == max(alias_lengths):
        return True
    return entity_name_length < max(alias_lengths)

def delete_duplicates(entities: list) -> list:
    """
        Supprimer les entités nommées qui sont des alias d'autres entités nommées
        On garde la plus grande entitée nommée, on merge les alias et on supprime les autres entités nommées
        Mettre le nom des alias à la place de leur id

        # Arguments
        * entities: liste des entités nommées d'un chapitre
    """

    data_cleaned = []

    #Parcourir la liste des entités pour mettre le nom des entités à la place de leur id
    for entity in entities:
        if len(entity['alias']) > 0:
            string_aliases = []
            for alias_id in entity['alias']:
                alias_name = entities[alias_id]['name']
                string_aliases.append(alias_name)
            entity['alias'] = string_aliases

    entities = [entity for entity in entities if not is_shorter_named_entity(entity)]
    return (entities)

def show_result(chapitre: list) -> list:
    """
        Afficher les résultats de chaque chapitre

        # Arguments
        * chapitre: liste des entités nommées d'un chapitre
    """
    for result in chapitre:
        print(result['name'])
        if (len(result['alias']) > 0):
            print(result['alias'])


def split_text_by_tokens(text: str, token_limit=500) -> list: 
    """
        Séparer le texte en sous-textes de 500 tokens

        # Arguments
        * text: texte à séparer
        * token_limit: nombre de tokens maximum par sous-texte (500 par défaut)
    """
    tokens = text.split(' ')
    
    token_chunks = []
    current_chunk = []

    for token in tokens:
        current_chunk.append(token)
        if len(current_chunk) >= token_limit:
            token_chunks.append(' '.join(current_chunk))
            current_chunk = []

    if current_chunk:
        token_chunks.append(' '.join(current_chunk))

    return token_chunks

def add_to_dictionnary(chapter: list) -> list:
    """
        Ajouter les nouvelles entités nommées au dictionnaire
            -si une entitée du chapitre est déjà dans le dictionnaire on ne l'ajoute pas
            -sinon on l'ajoute
            -si une entité du chapitre est déjà en temps qu'alias dans le dictionnaire on ne l'ajoute pas
                mais on ajoute ses alias à l'entité déjà présente dans le dictionnaire

        # Arguments
        * chapter: liste des entités nommées d'un chapitre
    """

    if not os.path.exists(path_dictionnary) or os.path.getsize(path_dictionnary) == 0:
        dictionary = []
    else:
        try:
            with open(path_dictionnary, "r", encoding="utf-8") as f:
                dictionary = json.load(f)
        except json.JSONDecodeError:
            print("Le fichier JSON est invalide ou vide.")
            dictionary = []

    alias_set = set()
    for entry in dictionary:
        alias_set.update(entry['alias'])

    for new_entity in chapter:
        new_name = new_entity['name']
        new_aliases = set(alias for alias in new_entity['alias'])

        # Cas 1: Nouvelle entité a le même nom qu'une entité du dictionnaire
        found = False
        for entry in dictionary:
            if new_name == entry['name']:
                entry['alias'] = list(set(entry['alias']) | new_aliases)
                found = True
                print ('\033[93m' + new_name + '\033[0m' + ' existe déjà et on a merge les alias')
                break

        # Cas 2: Nouvelle entité est dans une liste d'alias d'une entité du dictionnaire
        if not found:
            for entry in dictionary:
                if new_name in entry['alias']:
                    entry['alias'] = list(set(entry['alias']) | new_aliases)
                    found = True
                    print ('\033[91m' + new_name + '\033[0m' + ' est un alias de ' + entry['name'] + ' et on a merge les alias')
                    break

        # Cas 3: Nouvelle entité a un alias correspondant à une entité existante ou à ses alias
        if not found:
            for entry in dictionary:
                for alias in entry['alias']:
                    for new_alias in new_aliases:
                        if pretraitement_dictionnary(alias, new_alias):
                            print (alias + ' est un alias de ' + new_alias + ' et on a merge les alias')
                            entry['alias'] = list(set(entry['alias']) | new_aliases | {new_entity['name']})
                            found = True
                            print ('\033[33m' + new_name + '\033[0m' + ' est un alias de ' + entry['name'] + ' et on a merge les alias')
                            break
                if found:
                    break

        # Cas 4: Si la nouvelle entité n'a pas été fusionnée, l'ajouter simplement au dictionnaire
        if not found:
            dictionary.append({'id': len(dictionary), 'name': new_name, 'alias': list(new_aliases)})
            print ('\033[32m' + new_name + '\033[0m' + ' a été ajouté au dictionnaire')

    with open(path_dictionnary, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=4)

def clean_dictionary(dictionary: list) -> list:
    """
        Nettoyer le dictionnaire

        # Arguments
        * dictionnary: liste des entités nommées d'un chapitre
    """
    to_delete = []

    for entry in dictionary:
        for entry2 in dictionary:
            if pretraitement_dictionnary(entry['name'], entry2['name']) and entry['id'] != entry2['id'] and entry2 not in to_delete and entry not in to_delete:
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


def clean_chapter(chapter: list) -> list:
    """
        Nettoyer les chapitres en fusionnant les entités nommées qui sont similaires
        tout en s'aidant du dictionnaire commun précedement créé

        # Arguments
        * chapter: liste des entités nommées d'un chapitre
    """

    if not os.path.exists(path_dictionnary) or os.path.getsize(path_dictionnary) == 0:
        dictionary = []
    else:
        try:
            with open(path_dictionnary, "r", encoding="utf-8") as f:
                dictionary = json.load(f)
        except json.JSONDecodeError:
            print("Le fichier JSON est invalide ou vide.")
            dictionary = []

    to_remove = []
    ban_list = ['Dors Venabili','Maîtresse Venabili']
        
    for chapt in chapter:
        for entry in dictionary:
            for entry_alias in entry['alias']:
                if (pretraitement_chapter(chapt['name'], entry_alias) or pretraitement_chapter(entry['name'], chapt['name'])) and chapt not in to_remove:
                    for chapt2 in chapter:

                        if pretraitement_chapter(chapt2['name'], entry_alias) and chapt2 not in to_remove and chapt2 != chapt:
                            chapt['alias'] = list(set(chapt['alias']) | set(chapt2['alias']))
                            if (chapt2['name'] not in chapt['alias']):
                                chapt['alias'].append(chapt2['name'])
                            print('On supprime ' + chapt2['name'] + ' et on ajoute ses alias à ' + chapt['name'])
                            to_remove.append(chapt2)
                            break

                        if  pretraitement_chapter(entry['name'], chapt2['name']) and chapt2 not in to_remove and (not pretraitement_chapter(chapt['name'], chapt2['name']) and (chapt['name'] not in ban_list and chapt2['name'] not in ban_list)):
                            chapt['alias'] = list(set(chapt['alias']) | set(chapt2['alias']))
                            if (chapt2['name'] not in chapt['alias']):
                                chapt['alias'].append(chapt2['name'])
                            print('On supprime ' + chapt2['name'] + ' et on ajoute ses alias à ' + chapt['name'])
                            to_remove.append(chapt2)
                            break
    
    # Supprimer les entrées qui ont été fusionnées
    for entry in to_remove:
        chapter.remove(entry)

    return chapter


def main():
    """
        Partir d'un texte brut et extraire les entités nommées grace à un NER
        Créer un dictionnaire commun d'entités nommées / le nettoyer
        Nettoyer les chapitres en fusionnant les entités nommées qui sont similaires
    """
    # ETAPE 0: Initialisation du modèle NER
    tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/camembert-ner")
    model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    #Suppresion du dictionnaire actuel
    with open(path_dictionnary, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

    # ETAPE 1: Création du dictionnaire grace aux chapitres

    #Premier Livre : Les Cavernes d'Acier
    for file in os.listdir(path_caverne_normalized):
        file_path = os.path.join(path_caverne_normalized, file)
        output_file = file.replace(".txt", ".json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
            return
        ner_results = []

        #découper text en blocs de 500 mots car le modele NER ne prend que 500 mots à la fois
        chunks = split_text_by_tokens(text, 300)
        for i, chunk in enumerate(chunks, start=1):
            ner_results += (extract_REN(nlp,chunk))
        formatted_ner_results = format_ner_results(ner_results)

        with open(os.path.join(path_caverne_REN, output_file), "w", encoding="utf-8") as f:
            json.dump(formatted_ner_results, f, ensure_ascii=False, indent=4)
        add_to_dictionnary(formatted_ner_results)
        print(f"Traitement terminé pour {file_path}.")


    #Deuxieme Livre : Prelude à Fondation
    for file in os.listdir(path_prelude_normalized):

        file_path = os.path.join(path_prelude_normalized, file)
        output_file = file.replace(".txt", ".json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
            return
        ner_results = []

        #découper text en blocs de 500 mots car le modele NER ne prend que 500 mots à la fois
        chunks = split_text_by_tokens(text, 500)
        for i, chunk in enumerate(chunks, start=1):
            ner_results += (extract_REN(nlp,chunk))
        formatted_ner_results = format_ner_results(ner_results)

        with open(os.path.join(path_prelude_REN, output_file), "w", encoding="utf-8") as f:
            json.dump(formatted_ner_results, f, ensure_ascii=False, indent=4)
        add_to_dictionnary(formatted_ner_results)
        print(f"Traitement terminé pour {file_path}.")
        
    #ETAPE 2: Nettoyage du dictionnaire
    with open(path_dictionnary, "r", encoding="utf-8") as f:
        dictionary = json.load(f)
    clean_dictionary(dictionary)

    #ETAPE 3: Nettoyage des chapitres grace au dictionnaire

    #Premier livre : Les Cavernes d'Acier
    for file in os.listdir(path_caverne_REN):
        file_path = os.path.join(path_caverne_REN, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = json.load(f)
        except UnicodeDecodeError:
            print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
            return
        
        cleaned_text = clean_chapter(text)

        with open(os.path.join(file_path), "w", encoding="utf-8") as f:
            json.dump(cleaned_text, f, ensure_ascii=False, indent=4)
        print(f"{file_path} a été nettoyé.")
    

    #Deuxieme livre : Prelude à Fondation
    for file in os.listdir(path_prelude_REN):
        file_path = os.path.join(path_prelude_REN, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = json.load(f)
        except UnicodeDecodeError:
            print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
            return
        
        cleaned_text = clean_chapter(text)

        with open(os.path.join(file_path), "w", encoding="utf-8") as f:
            json.dump(cleaned_text, f, ensure_ascii=False, indent=4)
        print(f"{file_path} a été nettoyé.")

if __name__ == "__main__":
    main()
