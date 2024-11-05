import datetime
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

dotenv_path = os.getenv('DOTENV_PATH', '.env')
load_dotenv(dotenv_path)
api_key = os.environ.get("api_riot_key")
if api_key is None:
    raise ValueError("API key not found. Please set the 'api_riot_key' environment variable.")

# Setup retry strategy
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
# Fonction de base :
def get_puuid(gameName: str, tagLine: str):
    """
    Fetch the PUUID (Player Universal Unique Identifier) for a given player.

    Args:
        gameName (str): The game name of the player.
        tagLine (str): The tag line of the player.

    Returns:
        str: The PUUID of the player if found, otherwise None.
    """
    endpoint = f"/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
    try:
        url = urljoin(BASE_URL, endpoint + "?api_key=" + api_key)
        response = http.get(url)
        response.raise_for_status()
        return response.json().get("puuid")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PUUID: {e}")
        return None

root_url = "https://europe.api.riotgames.com"

def get_match_data_from_Id(matchId=None):
    """
    Fetch match data from Riot Games API using the match ID.

    Args:
        matchId (str): The ID of the match to fetch data for.

    Returns:
        dict: A dictionary containing match data if the request is successful.
        None: If there is an error in fetching the match data.
    """
    endpoint = f"/lol/match/v5/matches/{matchId}"
    try:
        url = urljoin(root_url, endpoint + '?api_key=' + api_key)
        response = http.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching match data: {e}")
        return None

def find_index_match_player(match, player_puuid_searched: str):
    """
    Find the index of a player in a match based on their PUUID.

    Args:
        match (dict): The match data.
        player_puuid_searched (str): The PUUID of the player to find.

    Returns:
        int: The index of the player in the match if found, otherwise None.
    """
    try:
        match_puuid_participants = match["metadata"]["participants"]
        index_player = match_puuid_participants.index(player_puuid_searched)
        return int(index_player)
    except ValueError as e:
        print(f"Error finding player index: {e}")
        return None

# Toutes les autres que j'utilise souvent :
        print(f"Error finding player index: {e}")
        return None
        return player_index - 5

# Toutes les autres que j'utilise souvent :
def get_match_Id(gameName: str, tagLine: str, champName: str = None, start_game: int = 0):
    """
    Récupère les ID des matchs basés sur les critères donnés.
    """
    puuid = get_puuid(gameName=gameName, tagLine=tagLine)
    list_matchs_ids = get_match_history(puuid=puuid, start=start_game, type="ranked")

    game_with_right_champ = []
    game_with_right_number = []
    
    nb_game_in_list = 0
    duration_minimum = 15

    # Parcourir tous les matchs récupérés
    for match_id in list_matchs_ids:
        game = get_match_data_from_Id(matchId=match_id)
        index_player = find_index_match_player(match=game, player_puuid_searched=puuid)
        
        if index_player is None:
            continue

        game_duration = round(game["info"]["gameDuration"] / 60)
        championName = game["info"]["participants"][index_player]["championName"]

        # Vérifier la durée du match
        if game_duration >= duration_minimum:
            nb_game_in_list += 1

            # Ajouter le match à la bonne liste (avec ou sans filtre sur le champion)
            if champName is None:
                game_with_right_number.append(match_id)
            elif championName == champName:
                game_with_right_champ.append(match_id)

    # Si on filtre par champion, on renvoie les matchs avec ce champion
    if champName:
        return game_with_right_champ
    else:
        return game_with_right_number
    
def info_par_role(gameName:str, tagLine:str, start_game:int, index_role:list[int,int] ,champName:str = None):
    """ Donne des informations en fonction des rôles.
     
    Args:
        gameName:str = Le nom du joueur
        tagLine:str = l'hashtag du joueur
        start_game:int 
        index_role:list[int,int] = Doit être donné par pair afin d'avoir uniquement les games jouer à ce rôle 
        champName:str = Doit donner le nom d'un champion
     """

    puuid = get_puuid(gameName = gameName, tagLine = tagLine)
    match_history = get_match_Id(gameName=gameName, tagLine=tagLine, start_game = start_game, champName = champName)
    df = pd.DataFrame()

    for match_id in match_history:
        game = get_match_data_from_Id(match_id)
        index_player = find_index_match_player(match=game, player_puuid_searched=puuid)
        if index_player not in index_role or index_player is None:
            continue

        info = game.get("info", {})
        participants = info.get("participants", [])
        player_stats = participants[index_player]
        game_data = extract_game_data(info, player_stats, index_player)
        df = pd.concat([df, game_data], ignore_index=True)

    return df

def extract_game_data(info, player_stats, index_player):
    gameDuration = round(info["gameDuration"]/60)
    riotIdGameName = player_stats["riotIdGameName"]
    champName = player_stats["championName"]
    win = player_stats["win"]
    gameStartTimestamp = datetime.datetime.fromtimestamp(info["gameStartTimestamp"]/1000).strftime("%d/%m/%Y")
    kills = player_stats["kills"]
    deaths = player_stats["deaths"]
    assists = player_stats["assists"]
    visionscore = player_stats["visionScore"]
    total_sbires = player_stats["totalMinionsKilled"] + player_stats["neutralMinionsKilled"]
    totalDamageDealtToChampions = player_stats["totalDamageDealtToChampions"]
    goldEarned = player_stats["goldEarned"]
    champExperience = player_stats["champExperience"]
    neutralMinionsKilled = player_stats["neutralMinionsKilled"]
    total_ping = calculate_total_ping(player_stats)
    total_ward_killed = player_stats["challenges"]["wardTakedowns"] + player_stats["wardsKilled"]
    wardsPlaced = player_stats["wardsPlaced"]
    nb_ward_bought = player_stats["sightWardsBoughtInGame"] + player_stats["visionWardsBoughtInGame"]
    controlWardsPlaced = player_stats["challenges"]["controlWardsPlaced"]
    team_indices = range(0, 5) if index_player < 5 else range(5, 10)
    team_total_kills = sum(info["participants"][i]["kills"] for i in team_indices)
    team_total_gold = sum(info["participants"][i]["goldEarned"] for i in team_indices)
    gold_percentage = f"{round((goldEarned/team_total_gold) * 100)}%"
    player_kp_percentage = round((kills + assists) / team_total_kills * 100 if team_total_kills > 0 else 0)
    player_kp_with_percentage = f"{player_kp_percentage}%"

    role_data = {
        "Nom du joueur": [riotIdGameName],
        "Date de la game": [gameStartTimestamp],
        "Durée de la game": [gameDuration],
        "champName": [champName],
        "kills": [kills],
        "deaths": [deaths],
        "assists": [assists],
        "total sbires tués": [total_sbires],
        "Total DMG": [totalDamageDealtToChampions],
        "Total Gold": [goldEarned],
        "Gold%": [gold_percentage],
        "Total XP": [champExperience],
        "Vision Score": [visionscore],
        "total_ping": [total_ping],
        "%KP": [player_kp_with_percentage],
        "win": [win],
    }

    if index_player in [1, 6]:  # Jungler
        role_data.update({
            "nb_ward_achetée": [nb_ward_bought],
            "wardsPlaced": [wardsPlaced],
            "Ward killed": [total_ward_killed],
            "Monstres tués": [neutralMinionsKilled],
        })
    elif index_player in [4, 9]:  # Support
        role_data.update({
            "wardsPlaced": [wardsPlaced],
            "Ward killed": [total_ward_killed],
            "Pink ward placed": [controlWardsPlaced],
        })

    return pd.DataFrame(role_data)

def calculate_total_ping(player_stats):
    return sum([
        player_stats["assistMePings"],
        player_stats["commandPings"],
        player_stats["enemyMissingPings"],
        player_stats["enemyVisionPings"],
        player_stats["holdPings"],
        player_stats["getBackPings"],
        player_stats["needVisionPings"],
        player_stats["onMyWayPings"],
        player_stats["pushPings"],
        player_stats["visionClearedPings"],
    ])

# Pour la timeline
def get_timeline(match_id:str):
    root = "https://europe.api.riotgames.com"
    endpoint = f"/lol/match/v5/matches/{match_id}/timeline"
    return http.get(root + endpoint + "?api_key=" + api_key).json()
def get_match_history(puuid, start=0, type="ranked"):
    root_url = "https://europe.api.riotgames.com"
    endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        "start": start,
        "type": type,
        "api_key": api_key
    }
    try:
        response = http.get(root_url + endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching match history: {e}")
        return []

def db_game_data(gameName:str, tagLine:str, champName:str = None, span:int = 10, count:int = 50):
    raw_db = pd.DataFrame()
    for i in range(0, count, span):
        match_ids = get_match_Id(gameName=gameName, tagLine=tagLine, champName=champName, start_game=i)
        for match_id in match_ids:
            game_data = get_match_data_from_Id(match_id)
            if game_data:
                raw_db = pd.concat([raw_db, pd.DataFrame([game_data])], ignore_index=True)
            time.sleep(1)
    return raw_db

def get_resume_game(gameName:str, tagLine:str, champName:str, start_game:int, number_of_games:int):
    """
    Retrieve a summary of game data for a specific player and champion over a number of games.

    Args:
        gameName (str): The game name of the player.
        tagLine (str): The tag line of the player.
        champName (str): The name of the champion.
        start_game (int): The starting game index.
        number_of_games (int): The number of games to retrieve.

    Returns:
        pd.DataFrame: A DataFrame containing the summary of game data.
    """
    raw_db = db_game_data(gameName=gameName, tagLine=tagLine, champName=champName, span=number_of_games, count=start_game + number_of_games)
    if raw_db.empty:
        return pd.DataFrame()

    player_index = find_index_match_player(raw_db.iloc[0], get_puuid(gameName, tagLine))
    if player_index is None:
        return pd.DataFrame()

    team_indices = range(0, 5) if player_index < 5 else range(5, 10)
    all_kill = [raw_db["info"]["participants"][i]["kills"] for i in team_indices]

    df = pd.DataFrame()
    for _, game_data in raw_db.iterrows():
        team_total_kills = sum(game_data["info"]["participants"][i]["kills"] for i in team_indices)
        player_stats = game_data["info"]["participants"][player_index]
        player_kills = player_stats["kills"]
        player_assists = player_stats["assists"]
        player_name = player_stats["riotIdGameName"]
        total_kp_raw = player_kills + player_assists
        player_kp = round((total_kp_raw / team_total_kills) * 100, 2) if team_total_kills > 0 else 0
        
        df = pd.concat([df, pd.DataFrame({
            "team": ["blue" if player_index < 5 else "red"],
            "all_kills": [sum(all_kill)],
            "team_total_kills": [team_total_kills],
            "player_kills": [player_kills],
            "player_assists": [player_assists],
            "total_kp_raw": [total_kp_raw],
            "player_KP": [player_kp]
        })], ignore_index=True)

    return df

def get_user_info(gameName:str, tagLine:str):
    puuid = get_puuid(gameName=gameName, tagLine=tagLine)
    if puuid is None:
        return {"error": "PUUID not found"}
    url = f"{BASE_URL}/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}"
    response = http.get(url)
    return response.json()

BASE_URL = "https://europe.api.riotgames.com"
