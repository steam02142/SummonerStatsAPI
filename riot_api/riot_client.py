import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
base_url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"

def get_player_puuid(riot_id: str, tagline: str) -> str:
    # Fetch puuid of player given their Riot ID and tagline
    api_url = base_url + riot_id + '/' + tagline + '/' + '?api_key=' + api_key
    response = requests.get(api_url)
    player_puuid = response.json()['puuid']
    print("puuid = " + player_puuid)