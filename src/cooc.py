# Gestion des co-occurences
#
# Authors: Lahcène Belhadi <lahcene.belhadi@gmail.com>

import json
from typing import Any, Dict, List, Optional, Tuple
from custom_exceptions import EmptyFile
from dataclasses import dataclass

@dataclass
class NamedEntity:
    pos: int
    entity: Dict[Any, Any]

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
        
        f_entity: NamedEntity | None = None  # first encountered
        s_entity: NamedEntity | None = None  # second encountered
        pairs: Dict[Tuple[int, int], int] = {} 

        for pos, token in enumerate(tokens):
            # vérifie si le token appartient à une entité nommée
            if self.is_named_entity(token):
                if f_entity is None:
                    f_entity = self.get_named_entity_from_id(
                        self.get_named_entity_id(token), pos
                    )
                    continue

                if s_entity is None:
                    s_entity = self.get_named_entity_from_id(
                        self.get_named_entity_id(token), pos
                    )

                    # si l'entité nommée est celle qui suit le token de la
                    # première alors on skip car 2 entitées nommées ne sont 
                    # pas collées, ça veut juste dire que c'est le nom de
                    # famille de la première entité
                    if s_entity.pos - f_entity.pos == 1:
                        s_entity = None
                        continue

                    # compare la distance entre f et s
                    if s_entity.pos - f_entity.pos <= 25:
                        key: Tuple[int, int] = (f_entity.entity["id"], s_entity.entity["id"])
                        key_alt: Tuple[int, int] = (s_entity.entity["id"], f_entity.entity["id"])

                        if key in pairs:
                            pairs[key] += 1

                        elif key_alt in pairs:
                            pairs[key_alt] += 1

                        else:
                            pairs[key] = 1

                    # move to next
                    f_entity = s_entity
                    s_entity = None

        print(pairs)

    def is_named_entity(self, token: str) -> bool:
        """
        Indique si le token donné est une entité nommée
        """

        for entity in self.data:
            name: str = entity["name"]

            if token in name.split():
                return True

        return False

    def get_named_entity_id(self, token: str) -> Optional[int]:
        """
        Retourne l'id de l'entité nommée à partir du nom
        """

        for entity in self.data:
            name: str = entity["name"]
            
            if token in name.split():
                return entity["id"]

        return None

    def get_named_entity_from_id(self, id: int, pos: int) -> Optional[NamedEntity]:
        """
        Retourne une named entity en fonction de l'id
        """
        
        for entity in self.data:
            if entity["id"] == id:
                return NamedEntity(pos=pos, entity=entity)

        return None

