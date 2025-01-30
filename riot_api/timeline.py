import requests
import os
from dotenv import load_dotenv
from typing import List
import pprint
import json

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")

test_matchid = "NA1_5209966860"

def get_timeline(matchid, region):
    root_url = f"https://{region}.api.riotgames.com"
    endpoint_url = f"/lol/match/v5/matches/{matchid}/timeline?api_key={api_key}"
    response = requests.get(root_url + endpoint_url)
    timeline_json = response.json()

    return timeline_json

def parse_timeline(timeline_json):
    player_timeline = [] # in here I want the participant id, game name, champion name, and eventually coordinates for map

    info = timeline_json["info"]
    frames = info["frames"]

    # The index matches to the minute
    participant_timeline = frames[2]

    for frame in frames:
        participant_frames = frame["participantFrames"]
        timestamp = frame["timestamp"]

        print(f"gold: {participant_frames['1']["totalGold"]}")
        print(round(timestamp/60000))

    

def process_timeline(matchid, region):
    timeline_json = get_timeline(matchid, region)
    timeline_data = parse_timeline(timeline_json)


process_timeline(test_matchid, "americas")