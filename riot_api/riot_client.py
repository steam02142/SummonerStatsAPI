import requests
import os
from dotenv import load_dotenv
from typing import List
import pprint
import json

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
base_url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"



def get_player_puuid(riot_id, tagline):
    # Fetch puuid of player given their Riot ID and tagline
    api_url = base_url + riot_id + '/' + tagline + '/' + '?api_key=' + api_key
    response = requests.get(api_url)
    player_puuid = response.json()['puuid']
    return player_puuid

def get_recent_match_ids(puuid, num_matches):
    # Fetch most recent matches, up to num_matches (max 100) using puuid
    match_id_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={num_matches}&api_key={api_key}"
    response = requests.get(match_id_url)
    return response.json()

def get_match_data(puuid, num_matches):
    # Currently only works with one match for testing
    matches = get_recent_match_ids(puuid, num_matches)
    for match in matches:
        match_data_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match}?api_key={api_key}"
        response = requests.get(match_data_url)
        match_data = response.json()
        participant_index = match_data["metadata"]["participants"].index(puuid)
        participant_data = match_data["info"]["participants"][participant_index]

        titlecard_data = {
            "champion": participant_data['championName'],
            "damageDealtToChampions": participant_data['totalDamageDealtToChampions'],
            "win": participant_data['win']
        }
        
        return titlecard_data


print(get_match_data(get_player_puuid("wumpus", "1112"), 1))