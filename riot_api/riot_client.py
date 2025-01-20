import requests
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
base_url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"



def get_player_puuid(riot_id: str, tagline: str) -> str:
    # Fetch puuid of player given their Riot ID and tagline
    api_url = base_url + riot_id + '/' + tagline + '/' + '?api_key=' + api_key
    response = requests.get(api_url)
    player_puuid = response.json()['puuid']
    return player_puuid

def get_recent_match_ids(puuid: str, num_matches: int) -> List[str]:
    # Fetch most recent matches, up to num_matches (max 100) using puuid
    match_id_url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={num_matches}&api_key={api_key}"
    response = requests.get(match_id_url)
    return response.json()

def get_match_data(puuid: str, num_matches: int) -> List[str]:
    matches = get_recent_match_ids(puuid, num_matches)
    


print(get_recent_match_ids(get_player_puuid("wumpus", "1112"), 5))