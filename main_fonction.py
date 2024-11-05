from dotenv import load_dotenv
import os
import requests
import pandas as pd
import datetime
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

load_dotenv(r"D:\Python\Perso\Esport\venv\.env")

api_key = os.environ.get("api_riot_key")

# Fonction de base :
def get_puuid(gameName:str, tagLine:str):
    root = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
    endpoint = f"{gameName}/{tagLine}"
    return requests.get(root + endpoint + "?api_key=" + api_key).json()["puuid"]

def get_match_history(puuid:str, start: int, type:str):
    root_url = "https://europe.api.riotgames.com"
    endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
    query_params = f"?type={type}&?start={start}&count=50"
    return requests.get(root_url + endpoint + query_params + '&api_key=' + api_key).json()

def get_match_data_from_Id(matchId=None):
    root_url = "https://europe.api.riotgames.com"
    endpoint = f"/lol/match/v5/matches/{matchId}"
    return requests.get(root_url + endpoint + '?api_key=' + api_key).json()

# Trouver les index des joueurs :
def find_index_match_player(match,player_puuid_searched:str):
    match_puuid_participants = get_match_data_from_Id(match)["metadata"]["participants"]
    index_player = match_puuid_participants.index(player_puuid_searched)
    return int(index_player)

def find_index_opponent(player_index:int):
    if player_index <= 5:
        return player_index + 5
    else:
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
        
        if index_player == None:
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

    nb_game = 0

    for match_id in match_history:
        game = get_match_data_from_Id(match_id)
        index_player = find_index_match_player(match=game, player_puuid_searched=puuid)
        print(f"index_player : {index_player}")
        
        if index_player not in index_role:
            pass
        else:
            
            if index_player == None:
                pass

            try:
                info = game["info"]
            except:
                continue

            print(f"index_role : {index_role}")

            print(f"index player après if : {index_player}")

            participants = info["participants"]
            gameDuration = round(info["gameDuration"]/60)
            nb_game += 1

            #Nom du joueur : 
            riotIdGameName = participants[index_player]["riotIdGameName"]

            #Nom du champion : 
            champName = info["participants"][index_player]["championName"]

            # WIN/LOSE :
            win = participants[index_player]["win"]

            # Date de la game -> A REVOIR PAS SUR 
            gameStartTimestamp = datetime.datetime.fromtimestamp(info["gameStartTimestamp"]/1000).strftime("%d/%m/%Y")
            # KDA :
            kills = participants[index_player]["kills"]
            deaths = participants[index_player]["deaths"]
            assists = participants[index_player]["assists"]
            

            # VisionScore
            visionscore = participants[index_player]["visionScore"]

            # totalsbires + les quelques jgl
            total_sbires = participants[index_player]["totalMinionsKilled"] + participants[index_player]["neutralMinionsKilled"]

            #TotalDMG
            totalDamageDealtToChampions = participants[index_player]["totalDamageDealtToChampions"]

            # Gold% :
            goldEarned = participants[index_player]["goldEarned"]
            
            # XP :
            champExperience = participants[index_player]["champExperience"]

            # Jungle sbire :
            neutralMinionsKilled = participants[index_player]["neutralMinionsKilled"]

            #Total ping dans la game :
            assistMePings = participants[index_player]["assistMePings"]
            commandPings = participants[index_player]["commandPings"]
            enemyMissingPings = participants[index_player]["enemyMissingPings"]
            enemyVisionPings = participants[index_player]["enemyVisionPings"]
            holdPings = participants[index_player]["holdPings"]
            getBackPings = participants[index_player]["getBackPings"]
            needVisionPings = participants[index_player]["needVisionPings"]
            onMyWayPings = participants[index_player]["onMyWayPings"]
            pushPings = participants[index_player]["pushPings"]
            visionClearedPings = participants[index_player]["visionClearedPings"]
            total_ping = assistMePings + commandPings + enemyMissingPings + enemyVisionPings + holdPings + getBackPings + needVisionPings + onMyWayPings + pushPings + visionClearedPings

            # Ward : 
            total_ward_killed = participants[index_player]["challenges"]["wardTakedowns"] + participants[index_player]["wardsKilled"]
            wardsPlaced = participants[index_player]["wardsPlaced"] # Toutes les wards sont comptées
            nb_ward_bought = participants[index_player]["sightWardsBoughtInGame"] + participants[index_player]["visionWardsBoughtInGame"]
            
            controlWardsPlaced = participants[index_player]["challenges"]["controlWardsPlaced"]

            # Total kill du joueur : 
            if index_player in range(0, 5):
                team_indices = range(0, 5)  # Blue side
            else:
                team_indices = range(5, 10)  # Red side

            team_total_kills = sum(participants[i]["kills"] for i in team_indices)
            team_total_gold = sum(participants[i]["goldEarned"] for i in team_indices)
            gold_percentage = f"{round((goldEarned/team_total_gold) * 100)}%"

            player_kp_percentage = round((kills + assists) / team_total_kills * 100 if team_total_kills > 0 else 0)
            
            # J'essaie d'avoir le nombre 
            player_kp_with_percentage = f"{player_kp_percentage}%"

            # Pour le top laner
            if index_player == 0 or index_player == 5:
                top_df = pd.DataFrame({"Nom du joueur" : [riotIdGameName],
                                        "Date de la game" : [gameStartTimestamp],
                                        "Durée de la game" : [gameDuration],
                                        "champName" : [champName],
                                        "kills" : [kills],
                                        "deaths" : [deaths],
                                        "assists" : [assists],
                                        "total sbires tués" : [total_sbires],
                                        "Total DMG" : [totalDamageDealtToChampions],
                                        "Total Gold" : [goldEarned],
                                        "Gold%" : [gold_percentage],
                                        "Total XP" : [champExperience],
                                        "Vision Score" : [visionscore],
                                        "total_ping" : [total_ping],
                                        "%KP" : [player_kp_with_percentage],
                                        "win" : [win],
                })
                df = pd.concat([df, top_df], ignore_index=True)
            
            # Pour le jungler :
            elif index_player == 1 or index_player == 6:
                jungle_df = pd.DataFrame({"Nom du joueur" : [riotIdGameName],
                                        "Date de la game" : [gameStartTimestamp],
                                        "Durée de la game" : [gameDuration],
                                        "champName" : [champName],
                                        "kills" : [kills],
                                        "deaths" : [deaths],
                                        "assists" : [assists],
                                        "nb_ward_achetée" : [nb_ward_bought],
                                        "wardsPlaced" : [wardsPlaced], # Ward normal
                                        "Ward killed" : [total_ward_killed],
                                        "Monstres tués" : [neutralMinionsKilled],
                                        "Total DMG" : [totalDamageDealtToChampions],
                                        "Total Gold" : [goldEarned],
                                        "Gold%" : [gold_percentage],
                                        "Total XP" : [champExperience],
                                        "Vision Score" : [visionscore],
                                        "total_ping" : [total_ping],
                                        "%KP" : [player_kp_with_percentage],
                                        "win" : [win],

                })
                df = pd.concat([df, jungle_df],ignore_index=True)

            # Pour le mid :
            elif index_player == 2 or index_player == 7:
                mid_df = pd.DataFrame({"Nom du joueur" : [riotIdGameName],
                                        "Date de la game" : [gameStartTimestamp],
                                        "Durée de la game" : [gameDuration],
                                        "champName" : [champName],
                                        "kills" : [kills],
                                        "deaths" : [deaths],
                                        "assists" : [assists],
                                        "total sbires tués" : [total_sbires],
                                        "Total DMG" : [totalDamageDealtToChampions],
                                        "Total Gold" : [goldEarned],
                                        "Gold%" : [gold_percentage],
                                        "Total XP" : [champExperience],
                                        "Vision Score" : [visionscore],
                                        "total_ping" : [total_ping],
                                        "%KP" : [player_kp_with_percentage],
                                        "win" : [win],
                })
                df = pd.concat([df, mid_df],ignore_index=True)
            
            # Pour l'ADC :
            elif index_player == 3 or index_player == 8:
                adc_df = pd.DataFrame({"Nom du joueur" : [riotIdGameName],
                                        "Date de la game" : [gameStartTimestamp],
                                        "Durée de la game" : [gameDuration],
                                        "champName" : [champName],
                                        "kills" : [kills],
                                        "deaths" : [deaths],
                                        "assists" : [assists],
                                        "total sbires tués" : [total_sbires],
                                        "Total DMG" : [totalDamageDealtToChampions],
                                        "Total Gold" : [goldEarned],
                                        "Gold%" : [gold_percentage],
                                        "Total XP" : [champExperience],
                                        "Vision Score" : [visionscore],
                                        "total_ping" : [total_ping],
                                        "%KP" : [player_kp_with_percentage],
                                        "win" : [win],
                })
                df = pd.concat([df, adc_df],ignore_index=True)

            # Pour le support :
            elif index_player == 4 or index_player == 9:
                support_df = pd.DataFrame({"Nom du joueur" : [riotIdGameName],
                                        "Date de la game" : [gameStartTimestamp],
                                        "Durée de la game" : [gameDuration],
                                        "champName" : [champName],
                                        "kills" : [kills],
                                        "deaths" : [deaths],
                                        "assists" : [assists],
                                        "wardsPlaced" : [wardsPlaced], # Ward normal
                                        "Ward killed" : [total_ward_killed],
                                        "Pink ward placed" : [controlWardsPlaced],
                                        "Vision Score" : [visionscore],
                                        "Total XP" : [champExperience],
                                        "total_ping" : [total_ping],
                                        "%KP" : [player_kp_with_percentage],
                                        "win" : [win],
                })
                df = pd.concat([df, support_df],ignore_index=True)
    return df

# Pour la timeline
def get_timeline(match_id:str):
    root = "https://europe.api.riotgames.com"
    endpoint = f"/lol/match/v5/matches/{match_id}/timeline"
    return requests.get(root + endpoint + "?api_key=" + api_key).json()

def db_game_data(gameName:str, tagLine:str, champName:str = None, span:int = None ,count:int = None, nb_of_games:int = None):
    """Ca garde en mémoire le nombre de game que tu veux. 
        Ca attend 10 secondes pour éviter que ça crash.

    Args : 
    ganeName:str = Nom de la personne
    tagLine:str = le # de la personne
    champName:str = le champion voulu, il est pas obligé de le mettre.
    span:int = le nombre d'espacement, doit être le même ou un multiple de count !
    count:int = Le nombre de game que tu veux
    number_of_games: int = Le nombre de game que la fonction va chercher
    """
    
    raw_db = pd.DataFrame()
    for i in range(0,count,span):
        resume_game = get_resume_game(gameName=gameName, tagLine=tagLine, champName=champName, start_game=i, number_of_games=nb_of_games)
        raw_db  = pd.concat([raw_db,resume_game])
        time.sleep(10)
    return raw_db

def get_resume_game(gameName:str, tagLine:str, champName:str = None, start_game:int = None, number_of_games:int = None, nb_game_limit:int = None):
    
    puuid_player = get_puuid(gameName = gameName, tagLine = tagLine)
    
    match_history = get_match_Id(gameName=gameName, tagLine=tagLine,champName = champName,start_game = start_game, number_of_games = number_of_games, nb_game_limit = nb_game_limit)
    df = pd.DataFrame()

    for id in match_history:
        game = get_match_data_from_Id(id)
        timeline = get_timeline(match_id=id)
        participants = game["info"]["participants"]
        index_player = find_index_match_player(match = game, player_puuid_searched=puuid_player)
        index_player_tl = index_player + 1
        index_opponent_tl = find_index_opponent(index_player_tl)

        timeline_frame = timeline["info"]["frames"]
        gameDuration_minute = round(game["info"]["gameDuration"]/60)
            
        # Name player :
        riotIdGameName_player = participants[index_player]["riotIdGameName"]
        # CS diff@5-10-15 :
        cs_diff5 = timeline_frame[5]["participantFrames"][str(index_player_tl)]["minionsKilled"] - timeline_frame[5]["participantFrames"][str(index_opponent_tl)]["minionsKilled"]
        cs_diff10 = timeline_frame[10]["participantFrames"][str(index_player_tl)]["minionsKilled"] - timeline_frame[10]["participantFrames"][str(index_opponent_tl)]["minionsKilled"]

        cs_diff15 = timeline_frame[15]["participantFrames"][str(index_player_tl)]["minionsKilled"] - timeline_frame[15]["participantFrames"][str(index_opponent_tl)]["minionsKilled"]
        gold_diff14 = timeline_frame[15]["participantFrames"][str(index_player_tl)]["totalGold"] - timeline_frame[14]["participantFrames"][str(index_opponent_tl)]["totalGold"]
        xp_diff = timeline["info"]["frames"][15]["participantFrames"][str(index_player_tl)]["xp"] - timeline["info"]["frames"][14]["participantFrames"][str(index_opponent_tl)]["xp"]
            
        # Gold diff@5-10-15 :
        gold_diff5 = timeline_frame[5]["participantFrames"][str(index_player_tl)]["totalGold"] - timeline_frame[5]["participantFrames"][str(index_opponent_tl)]["totalGold"]
        gold_diff10 = timeline_frame[10]["participantFrames"][str(index_player_tl)]["totalGold"] - timeline_frame[10]["participantFrames"][str(index_opponent_tl)]["totalGold"]
    
            # Avoir le CS/M :
        totalMinionsKilled = participants[index_player]["totalMinionsKilled"] + participants[index_player]["neutralMinionsKilled"]
        csm = round(totalMinionsKilled/gameDuration_minute, 2)

            # Avoir le DPM :
        totalDamageDealtToChampions = participants[index_player]["totalDamageDealtToChampions"]
        dpm = round(totalDamageDealtToChampions/gameDuration_minute)

            # Avoir le nombre de kill et assists et KDA:
        kill = participants[index_player]["kills"]
        deaths = participants[index_player]["deaths"]
        assists = participants[index_player]["assists"]
        if deaths == 0:
            kda_moy = round(kill+assists,2)
        else:
            kda_moy = round((kill+assists)/deaths,2)

        # KP :
        if index_player in range(0, 5):
            team_indices = range(0, 5)  # Blue side
        else:
            team_indices = range(5, 10)  # Red side

        team_total_kills = sum(participants[i]["kills"] for i in team_indices)

        player_kp_percentage = round((kill + assists) / team_total_kills * 100 if team_total_kills > 0 else 0, 2)
        player_kp_with_percentage = f"{player_kp_percentage}%"
        
        # Champion name : 
        championName = participants[index_player]["championName"]

        match_DF = pd.DataFrame({"Riot name" : [riotIdGameName_player],
                            "Champion Name" : [championName],
                            "durée game" : [gameDuration_minute],
                            "Kill" : [kill],
                            "Death" : [deaths],
                            "Assist" : [assists],
                            "kda" : [kda_moy],
                            "DPM" : [dpm],
                            "CS/M" : [csm],
                            "CS@5" : [cs_diff5],
                            "CS@10" : [cs_diff10],
                            "CS@15" : [cs_diff15],
                            "Gold@5" : [gold_diff5],
                            "Gold@10" : [gold_diff10],
                            "Gold@15" : [gold_diff14],
                            "XP@14" : [xp_diff],
                            "KP" : [player_kp_with_percentage], 
        })
    
        df = pd.concat([df, match_DF], ignore_index=False)

    return df

def get_kp_for_player(game_data, player_index):
    # Vérification de l'équipe (Blue side: index 0 à 4, Red side: index 5 à 9)
    if player_index in range(0, 5):
        team = 'Blue'
        team_indices = range(0, 5)  # Blue side
    else:
        team = 'Red'
        team_indices = range(5, 10)  # Red side

    all_kill = []
    for a in range(0,10):
        all_kill.append(game_data["info"]["participants"][a]["kills"])
    

    # Calcul du nombre total de kills pour l'équipe
    team_total_kills = sum(game_data["info"]["participants"][i]["kills"] for i in team_indices)

    # Kills et assists du joueur
    player_stats = game_data["info"]["participants"][player_index]
    player_kills = player_stats["kills"]
    player_assists = player_stats["assists"]
    player_name = player_stats["riotIdGameName"]
    riotIdTagline = player_stats["riotIdTagline"]

    # Calcul du Kill Participation (KP)
    total_kp_raw = (player_kills + player_assists)
    player_kp = round((player_kills + player_assists) / team_total_kills * 100 if team_total_kills > 0 else 0, 2)

    df = pd.DataFrame(data={
        "player_name" : [player_name],
        "player_ID" : [riotIdTagline],
        "team": [team],
        "all_kills" : [sum(all_kill)],
        "team_total_kills": [team_total_kills],
        "player_kills": [player_kills],
        "player_assists": [player_assists],
        "total_kp_raw" : [total_kp_raw],
        "player_KP": [player_kp]  # Arrondir à 2 décimales
    })

    return df

def get_match_participants(match_id):
    # Remplacez cette URL avec l'URL correcte pour obtenir les participants du match
    url = f"{BASE_URL}/lol/match/v5/matches/{match_id}?api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    participants = []
    for participant in data['info']['participants']:
        participants.append(participant['puuid'])
    
    return participants

def get_user_info(gameName:str,tagLine:str):
    puuid = get_puuid(gameName=gameName,tagLine=tagLine)
    base_url= "https://europe.api.riotgames.com"
    url = f"{base_url}/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}"
    response = requests.get(url)
    return response.json()["gameName"]







