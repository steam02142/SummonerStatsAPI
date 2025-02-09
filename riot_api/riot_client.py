import requests
import os
from dotenv import load_dotenv
from typing import List
import pprint
import json
from riot_api.cache import participant_data
from numerize import numerize 


load_dotenv()

api_key = os.getenv("RIOT_API_KEY")

def get_player_puuid(riot_id, tagline, region):
    # Fetch puuid of player given their Riot ID and tagline
    api_url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_id}/{tagline}?api_key={api_key}"
    response = requests.get(api_url)
    player_puuid = response.json()['puuid']
    return player_puuid

def get_recent_match_ids(puuid, num_matches, region):
    # Fetch most recent matches, up to num_matches (max 100) using puuid
    match_id_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={num_matches}&api_key={api_key}"
    response = requests.get(match_id_url)
    return response.json()

def get_match_data_from_id(matchid, region):
    root_url = f"https://{region}.api.riotgames.com"
    endpoint_url = f"/lol/match/v5/matches/{matchid}?api_key={api_key}"
    response = requests.get(root_url + endpoint_url)
    match_data = response.json()
    
    return match_data
    

def parse_match_data(puuid, match_json):
    parsed_data = {
        "all_players": [],
        "match_stats": None,
        "primary_player_stats": None
    }

    metadata = match_json['metadata']
    info = match_json['info']
    participants = metadata['participants']

    # json of all player specific info for all 10 players    
    players = info['participants']

    # get our player for further stats
    primary_player = players[participants.index(puuid)]
    
    parsed_data["match_stats"] = {
        "gameDuration": info["gameDuration"],
        "gameMode": info["gameMode"],
        "gameName": info["gameName"],
        "matchId": metadata["matchId"]
    }

    # get the names and champions of all the players in the game
    for player in players:
        damage = numerize.numerize(player["totalDamageDealtToChampions"], 1)
        gold = numerize.numerize(player["goldEarned"], 1)
        riotName = player['riotIdGameName']
        championId = player['championId']
        parsed_data["all_players"].append({
            "riotName": riotName,
            "championId": championId,
            "won": player["win"],
            "participantId": player["participantId"],
            "kills": player["kills"],
            "deaths": player["deaths"],
            "assists": player["assists"],
            "creepScore": player["totalMinionsKilled"],
            "damageDealt": damage,
            "gold": gold,
            "items": [
                player["item0"],
                player["item1"],
                player["item2"],
                player["item3"],
                player["item4"],
                player["item5"]
            ],
            "summoners": [
                player["summoner1Id"],
                player["summoner2Id"]
            ]
        })

    kill_participation_percentage = round(primary_player["challenges"]["killParticipation"]*100, 1)
    gold = numerize.numerize(primary_player["goldEarned"])
    damage = numerize.numerize(primary_player["totalDamageDealtToChampions"])

    parsed_data["primary_player_stats"] = {
        "riotName": primary_player["riotIdGameName"],
        "championId": primary_player["championId"],
        "playerLevel": primary_player["summonerLevel"],
        "championLevel": primary_player["champLevel"],
        "kills": primary_player["kills"],
        "deaths": primary_player["deaths"],
        "assists": primary_player["assists"],
        "won": primary_player["win"],
        "creepScore": primary_player["totalMinionsKilled"],
        "damageDealt": damage,
        "killParticipation": kill_participation_percentage,
        "gold": gold,
        
        "items": [
            primary_player["item0"],
            primary_player["item1"],
            primary_player["item2"],
            primary_player["item3"],
            primary_player["item4"],
            primary_player["item5"]
        ],
        "summoners": [
            primary_player["summoner1Id"],
            primary_player["summoner2Id"]
        ]
    }
    return parsed_data

def process_matches(puuid, num_matches, region):
    match_ids = get_recent_match_ids(puuid, num_matches, region)
    summoner_mapping = get_summoner_id_mapping()
    item_mapping = get_item_id_mapping()
    all_match_data = []

    for match_id in match_ids:
        match_data = get_match_data_from_id(match_id, region)
        parsed_match_data = parse_match_data(puuid, match_data)
        replace_summoners(parsed_match_data['primary_player_stats'], summoner_mapping)
        replace_items(parsed_match_data['primary_player_stats'], item_mapping)

        all_players = parsed_match_data['all_players']
        for player in all_players:
            replace_summoners(player, summoner_mapping)
            replace_items(player, item_mapping)

        all_match_data.append(parsed_match_data)
        add_champion_name_and_icon(parsed_match_data['all_players'], parsed_match_data['primary_player_stats'])
        cache_participant_data(parsed_match_data['all_players'], parsed_match_data['match_stats']["matchId"])

    return all_match_data

def get_summoner_id_mapping():
    summoners = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells.json"
    summoners_json = requests.get(summoners).json()

    summoners_dict = []
    for summoner in summoners_json:
        icon_url = "https://raw.communitydragon.org/latest/game/data/spells/icons2d/"
        icon_name = summoner['iconPath'].split('/')[::-1][0].lower()
        icon_url = icon_url + icon_name

        summoners_dict.append( {
            "id": summoner['id'],
            "name": summoner['name'],
            "icon": icon_url
        })
    
    return summoners_dict

def get_item_id_mapping():
    items = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/items.json"
    items_json = requests.get(items).json()

    items_dict = []
    for item in items_json:
        icon_url = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/items/icons2d/"
        icon_name = item['iconPath'].split('/')[::-1][0].lower()
        icon_url = icon_url + icon_name

        items_dict.append( {
            "id": item['id'],
            "name": item['name'],
            "icon": icon_url
        })
    
    return items_dict


def replace_items(player_data, item_mapping):
    item_dict = {item['id']: item for item in item_mapping}

    for i in range(len(player_data['items'])):
        if player_data['items'][i] != 0:  
            item_info = item_dict.get(player_data['items'][i])
            player_data['items'][i] = item_info 
        else:
            player_data['items'][i] = None

def replace_summoners(player_data, summoner_mapping):
    summoner_dict = {summoner['id']: summoner for summoner in summoner_mapping}

    for i in range(len(player_data['summoners'])):
        summoner_info =summoner_dict.get(player_data['summoners'][i])
        player_data['summoners'][i] = summoner_info

def add_champion_name_and_icon(all_players, primary_player):
    champions = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json"
    champion_portrait = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/"
    champions_json = requests.get(champions).json()
    champion_dict = {champion['id']: champion for champion in champions_json}

    for player in all_players:
        champion_data = champion_dict.get(player['championId'])
        icon_name = champion_data['squarePortraitPath'].split('/')[::-1][0]
        icon_path = champion_portrait + icon_name
        player.update({
            "champion_icon": icon_path,
            "championName": champion_data['name']
        })
    
    # for the primary player
    champion_data = champion_dict.get(primary_player['championId'])
    icon_name = champion_data['squarePortraitPath'].split('/')[::-1][0]
    icon_path = champion_portrait + icon_name
    primary_player.update({
        "champion_icon": icon_path,
        "championName": champion_data['name']
    })
    
    return champions_json

def cache_participant_data(all_players, matchId):
    participant_data[matchId] = all_players


def get_profile_icon(puuid, region):
    root_url = f"https://{region}.api.riotgames.com"
    endpoint_url = f"/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}"
    response = requests.get(root_url + endpoint_url)
    summoner_data = response.json()
    profile_id = summoner_data["profileIconId"]

    profile_icon_url = f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{profile_id}.jpg"

    
    return profile_icon_url
    

puuid = get_player_puuid("Wumpus", "1112", "americas")
print(puuid)

pprint.pprint(process_matches(puuid, 2, "americas"))