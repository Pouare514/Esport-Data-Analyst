# Esport-Data-Analyst

## Description
Esport-Data-Analyst est un projet Python qui permet de récupérer et analyser des données de jeu pour le jeu League of Legends en utilisant l'API de Riot Games. Le projet inclut des fonctionnalités pour obtenir des informations sur les joueurs, les matchs, et les statistiques détaillées des parties.

## Installation
1. Clonez le dépôt :
    ```bash
    git clone https://github.com/LorisRss/Esport-Data-Analyst
    cd Esport-Data-Analyst
    ```

2. Créez un environnement virtuel et activez-le :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
    ```

3. Installez les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

4. Créez un fichier `.env` à la racine du projet et ajoutez votre clé API Riot Games :
    ```env
    api_riot_key=VOTRE_CLE_API
    ```

## Utilisation
Voici quelques exemples d'utilisation des fonctions disponibles dans le projet.

### Récupérer le PUUID d'un joueur
```python
from main_fonction import get_puuid

gameName = "NomDuJoueur"
tagLine = "TagDuJoueur"
puuid = get_puuid(gameName, tagLine)
print(f"PUUID: {puuid}")
```

### Récupérer les données d'un match

```python
from main_fonction import get_match_data_from_Id

matchId = "ID_Du_Match"
match_data = get_match_data_from_Id(matchId)
print(match_data)
```
### Récupérer les statistiques d'un joueur par rôle
```python
from main_fonction import info_par_role

gameName = "NomDuJoueur"
tagLine = "TagDuJoueur"
start_game = 0
index_role = [0, 5]  # Exemple pour le rôle de top laner
champName = "NomDuChampion"

df = info_par_role(gameName, tagLine, start_game, index_role, champName)
print(df)
```
Récupérer l'historique des matchs d'un joueur
```python
from main_fonction import get_match_history

puuid = "PUUID_Du_Joueur"
match_history = get_match_history(puuid)
print(match_history)
```
Contribuer
Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour discuter des changements que vous souhaitez apporter.

Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. ```
