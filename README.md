# persograph
Pour lancer notre projet il faut executer la commande suivante:
```bash
python3 src/main.py
```

L'extraction d'entités nommées va alors commencer ainsi que le résolution d'alias.
Par la suite la détection d'intéraction à lieu et enfin un fichier my_submission.csv est updaté avec le graphe.

Il est nécessaire d'installer les différents packages pour lancer l'application:
- https://pypi.org/project/pandas/
- https://pypi.org/project/networkx/
- https://pypi.org/project/fuzzywuzzy/
- https://pypi.org/project/jaro-winkler/
