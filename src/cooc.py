# Gestion des co-occurences
#
# Authors: Lahcène Belhadi <lahcene.belhadi@gmail.com>

import json
from typing import Any, Dict, List, Tuple
from custom_exceptions import EmptyFile

class Cooc:
    """
    Gestion des co-occurences dans un texte
    """

    def __init__(self, path: str) -> None:
        """
        Créer une instance de `Cooc`

        # Arguments
        * path: `str` - le chemin vers le fichier JSON où se trouve les entités
        nommées
        """
        self.path: str = path
        self.data: Dict[str, str | int] = {}

        # la liste des co-occurences trouvées sous forme de paires de noms
        self.found: List[Tuple[str, str]] = []

    def __fetch_data(self) -> None:
        """
        Retrouve les entitées nommées depuis le fichier JSON assigné et les 
        stocke dans `self.data`

        # Raises
        * `FileNotFoundError` - retourne un `FileNotFoundError` si le fichier 
        * `EmptyFile` - retourne un `EmptyFile` si le fichier obtenu est vide
        * `JSONDecodeError` - retourne un `JSONDecodeError` si le contenu du 
        fichier JSON est malformé

        n'a pas pu être ouvert à partir de `self.path`
        """
        try:
            with open(self.path, 'w') as file:
                data: str = file.read()

                # si le fichier ne contient aucune données
                if data == '':
                    raise Exception(EmptyFile)
                
                try:
                    self.data = json.loads(data)
                
                except json.JSONDecodeError as error:
                    raise error

        except OSError:
            raise Exception(FileNotFoundError)

    def find(self) -> None:
        """
        Trouve les paires de co-occurences dans le texte à partir des entitées 
        nommées présentes dans le fichier JSON associé
        """

        try:
            self.__fetch_data()

        except Exception as error:
            print(f"Une erreur est survenue lors de l'extraction des données JSON: {error}")
            exit(1)

