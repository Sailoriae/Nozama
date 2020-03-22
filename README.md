# Nozama !

Nozama est un index d'alternatives à Amazon.

Cet index consiste en une page HTML générée par un script Python ! La base de données se trouve dans le fichier `base_de_données.csv`.

## Utilisation

Le déploiement est fait automatiquement par GitHub Actions, qui met tout dans la branche `gh-pages`, afin que la page soit disponible via GitHub Pages.

Cependant, si vous souhaitez l'héberger indépendemment, il vous suffit de :
- Installer les dépendances Python : `python3 -m pip install -r ./requirements.txt`
- Lancer le script : `python3 générer.py` (J'aime l'UTF-8)
