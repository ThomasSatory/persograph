import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# Le but de ce fichier est de prendre tout les fichiers du dossier res/corpus_asimov_leaderboard/les_cavernes_d_acier et du dossier 
# res/corpus_asimov_leaderboard/prelude_a_fondation et de les mettre dans un dossier res/corpus_asimov_leaderboard_normalized/les_cavernes_d_acier_normalized
# et res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized avec le même nom de fichier + normalized à la fin mais avec le texte normalisé

path_caverne = "../res/corpus_asimov_leaderboard/les_cavernes_d_acier"
path_prelude = "../res/corpus_asimov_leaderboard/prelude_a_fondation"

path_caverne_normalized = "../res/corpus_asimov_leaderboard_normalized/les_cavernes_d_acier_normalized"
path_prelude_normalized = "../res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized"

#fonction qui prend en entrée un fichier et le normalise
def normalize(file):
    file_path = os.path.join(path_caverne, file)  # Chemin complet du fichier
    output_file = file.replace(".txt.preprocessed", "_normalized.txt")  # Nom du fichier de sortie

    try:
        # Ouvrir le fichier en lecture avec l'encodage latin-1 (ISO-8859-1)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
        return

    #normaliser le texte
    normalized_text = clean_txt(text)

    #save les resultats dans un fichier txt dans le dossier res/corpus_asimov_leaderboard_normalized/les_cavernes_d_acier_normalized
    with open(os.path.join(path_caverne_normalized, output_file), "w", encoding="utf-8") as f:
        f.write(normalized_text)

    print(f"Traitement terminé pour {file_path}.")

def normalize_prelude(file):
    file_path = os.path.join(path_prelude, file)  # Chemin complet du fichier
    output_file = file.replace(".txt.preprocessed", "_normalized.txt")  # Nom du fichier de sortie

    try:
        # Ouvrir le fichier en lecture avec l'encodage utf-8 et lire seulement 300 caracteres par 300 caracteres
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        print(f"Impossible de lire le fichier {file_path}. Assurez-vous de l'encodage approprié.")
        return

    #normaliser le texte
    normalized_text = clean_txt(text)


    #save les resultats dans un fichier txt dans le dossier res/corpus_asimov_leaderboard_normalized/prelude_a_fondation_normalized
    with open(os.path.join(path_prelude_normalized, output_file), "w", encoding="utf-8") as f:
        f.write(normalized_text)

    print(f"Traitement terminé pour {file_path}.")

#Enlever tout les caractères spéciaux, remplacer les accents par les lettres correspondantes et garder les points fermant des phrases
def clean_txt(text):
    delete_stop_words(text)
    #remplacer les accents par les lettres correspondantes meme en majuscule
    text = text.replace('é', 'e')
    text = text.replace('è', 'e')
    text = text.replace('ê', 'e')
    text = text.replace('à', 'a')
    text = text.replace('â', 'a')
    text = text.replace('î', 'i')
    text = text.replace('ô', 'o')
    text = text.replace('û', 'u')
    text = text.replace('ù', 'u')
    text = text.replace('ç', 'c')
    text = text.replace('œ', 'oe')
    text = text.replace('æ', 'ae')
    text = text.replace('ï', 'i')
    text = text.replace('ë', 'e')
    text = text.replace('É', 'E')
    text = text.replace('È', 'E')
    text = text.replace('Ê', 'E')
    text = text.replace('À', 'A')
    text = text.replace('Â', 'A')
    text = text.replace('Î', 'I')
    text = text.replace('Ô', 'O')
    text = text.replace('Û', 'U')
    text = text.replace('Ù', 'U')
    text = text.replace('Ç', 'C')
    text = text.replace('Œ', 'OE')
    text = text.replace('Æ', 'AE')
    text = text.replace('Ï', 'I')
    text = text.replace('Ë', 'E')
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    return text

#Enlever les stop words grace à ntlk en francais
def delete_stop_words(text):
    stop_words = set(stopwords.words('french'))
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    #remettre sous la forme de texte et non de liste
    filtered_sentence = ' '.join(filtered_sentence)
    return filtered_sentence



def main():
    # Boucle sur tous les fichiers du corpus_pdf_directory
    for file in os.listdir(path_caverne):
        if file.endswith(".txt.preprocessed"):
            normalize(file)

    for file in os.listdir(path_prelude):
        if file.endswith(".txt.preprocessed"):
            normalize_prelude(file)

if __name__ == "__main__":
    main()