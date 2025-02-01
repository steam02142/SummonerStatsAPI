import requests
import os
from dotenv import load_dotenv
from typing import List
import pprint
import json
from riot_api.cache import participant_data

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")

def get_timeline(matchid, region):
    root_url = f"https://{region}.api.riotgames.com"
    endpoint_url = f"/lol/match/v5/matches/{matchid}/timeline?api_key={api_key}"
    response = requests.get(root_url + endpoint_url)
    timeline_json = response.json()

    return timeline_json

def parse_timeline(timeline_json):
    player_timeline = {i: {"totalGold": [], "minionsKilled":[], "damageStats":[]} for i in range(1,11)}


    info = timeline_json["info"]
    frames = info["frames"]

    # The tracks information for each minute of the game (a frame is 60 seconds)
    for frame in frames:
        participant_frames = frame["participantFrames"]
        timestamp = frame["timestamp"]
        # print(participant_frames)
        for participant_id in participant_frames:
            player_data = participant_frames[participant_id]
            player_timeline[int(participant_id)]["totalGold"].append(player_data["totalGold"])
            player_timeline[int(participant_id)]["minionsKilled"].append(player_data["minionsKilled"])
            player_timeline[int(participant_id)]["damageStats"].append(player_data["damageStats"])
    
    return player_timeline

    

def process_timeline(matchid, region):
    timeline_json = get_timeline(matchid, region)
    timeline_data = parse_timeline(timeline_json)

    # add cached data to the dictionary, allowing us to add extra information to graphs
    for participant_id in timeline_data:
        timeline_data[int(participant_id)].update(championData = participant_data[matchid][int(participant_id) - 1]) 
        # timeline_data[int(participant_id)].update(matchDuration = participant_data[matchid][int(participant_id) - 1]) 


    chart_data = transformForChart(timeline_data, matchid)

    return chart_data

def transformForChart(timeline_data, matchid):
    # Determine game duration from how many minutes we collected data about gold
    gameDuration = len(timeline_data[1]["totalGold"])
    
    chart_data = []

    for minute in range(gameDuration):
        minute_data = {"minute": minute}

        for index in range(1, 11):
            player_data = timeline_data[index]
            
            test = {}
            # store each of the desired chart values
            test[f"championName"] = participant_data[matchid][index- 1]["championName"]
            test[f"gold"] = player_data["totalGold"][minute]
            test[f"minionsKilled"] = player_data["minionsKilled"][minute]
            minute_data.update({f"player{index}": test})

         
        chart_data.append(minute_data)

    return chart_data
        



test_matchid = "NA1_5209966860"
process_timeline(test_matchid, "americas")