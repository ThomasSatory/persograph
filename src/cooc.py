# Gestion des co-occurences
#
# Authors: Lahcène Belhadi <lahcene.belhadi@gmail.com>

from collections.abc import Generator
from io import BytesIO
import json
import token
import tokenize
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
        self.data: List[Dict[str, str | int]] = []

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
            with open(self.path, 'r') as file:
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

    def __fetch_tokens(self, path: str) -> List[str]:
        """
        Lit le fichier texte donné et extrait les tokens

        # Arguments
        * path: `str` - le chemin ers le fichier texte

        # Raises
        * `FileNotFoundError` - retourne un `FileNotFoundError` si le fichier 
        """
        with open(path, 'r') as file:
            content = file.read().split()
            return content

    def find(self) -> None:
        """
        Trouve les paires de co-occurences dans le texte à partir des entitées 
        nommées présentes dans le fichier JSON associé
        """

        self.__fetch_data()

        tokens = self.__fetch_tokens("res/test/text.txt")
        self.algo(tokens)

    def algo(self, tokens: List[str]) -> None:
        """
        Trouve les pairs liées entre elles
        """
        # TODO: Au lieu de split le nom de toutes les entités nommées et de le 
        # mettre dans une liste, on vérifie pour chaque token s'il est dans 
        # la liste des entités nommées au format JSON (on fait un split sur le
        # nom au moment du check) pour toujours avoir un pointeur vers le JSON
        
        
