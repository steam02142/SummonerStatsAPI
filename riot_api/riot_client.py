import requests
import os
from dotenv import load_dotenv
from typing import List
import pprint
import json

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
    # Currently only works with one match for testing
    root_url = f"https://{region}.api.riotgames.com"
    endpoint_url = f"/lol/match/v5/matches/{matchid}?api_key={api_key}"
    response = requests.get(root_url + endpoint_url)
    match_data = response.json()
    
    return match_data
    

    # For card data we want:
        #Individually: champ, win, level, kill participation, KDA, game type, when it was played (x minutes/hours/days/months ago)
        #For the whole game: riotIdGameName, champ

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
    }

    # get the names and champions of all the players in the game
    for player in players:
        riotName = player['riotIdGameName']
        championName = player['championName']
        parsed_data["all_players"].append({
            "riotName": riotName,
            "championName": championName
        })



    parsed_data["primary_player_stats"] = {
        "championName": primary_player["championName"],
        "playerLevel": primary_player["summonerLevel"],
        "kills": primary_player["kills"],
        "deaths": primary_player["deaths"],
        "assists": primary_player["assists"],
        
        "item0": primary_player["item0"],
        "item1": primary_player["item1"],
        "item2": primary_player["item2"],
        "item3": primary_player["item3"],
        "item4": primary_player["item4"],
        "item5": primary_player["item5"],
        "summoner1": primary_player["summoner1Id"],
        "summoner2": primary_player["summoner2Id"]
    }
    # championName = players['championName']
    return parsed_data

def process_matches(puuid, num_matches, region):
    match_ids = get_recent_match_ids(puuid, num_matches, region)
    summoner_mapping = get_summoner_id_mapping()
    item_mapping = get_item_id_mapping()

    for match_id in match_ids:
        match_data = get_match_data_from_id(match_id, region)
        parsed_match_data = parse_match_data(puuid, match_data)
        # parsed match data is all the information we will be returning for each map. This will be packaged 
        # up in a json with multiple indexes 
        replace_summoners(parsed_match_data['primary_player_stats'], summoner_mapping)
        replace_items(parsed_match_data['primary_player_stats'], item_mapping)


        pprint.pprint(parsed_match_data['primary_player_stats'])

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
            # get the last portion of the 
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
            # get the last portion of the 
            "icon": icon_url
        })
    
    return items_dict

def replace_items(player_data, item_mapping):
    item_dict = {item['id']: item for item in item_mapping}

    for i in range(0, 6):
        item = f"item{i}"
        player_data[item] = item_dict.get(player_data[item], None)

    

def replace_summoners(player_data, summoner_mapping):
    summoner_dict = {summoner['id']: summoner for summoner in summoner_mapping}

    # Use `.get()` for efficient lookups
    player_data['summoner1'] = summoner_dict.get(player_data['summoner1'])
    player_data['summoner2'] = summoner_dict.get(player_data['summoner2'])




    


puuid = get_player_puuid("Wumpus", "1112", "americas")
print(puuid)
# last_match = get_recent_match_ids(puuid, 1, "americas")[0]


# pprint.pprint(get_match_data_from_id(last_match, "americas"))

process_matches(puuid, 1, "americas")

get_item_id_mapping()