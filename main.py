import requests

api_key = "RGAPI-dd530e91-0b60-458f-a9d3-83d5ee6b0972"
api_url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"

riot_id = "wumpus"
tagline = "1112"

api_url = api_url + riot_id + '/' + tagline + '/' + '?api_key=' + api_key
response = requests.get(api_url)

player_puuid = response.json()['puuid']

print(player_puuid)

