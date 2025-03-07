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
    player_timeline = {i: {"totalGold": [], "minionsKilled":[], "damageToChamps":[]} for i in range(1,11)}


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
            player_timeline[int(participant_id)]["damageToChamps"].append(player_data["damageStats"]["totalDamageDoneToChampions"])
    
    return player_timeline

    

def process_timeline(matchid, region):
    timeline_json = get_timeline(matchid, region)
    timeline_data = parse_timeline(timeline_json)

    # add cached data to the dictionary, allowing us to add extra information to graphs
    for participant_id in timeline_data:
        timeline_data[int(participant_id)].update(championData = participant_data[matchid][int(participant_id) - 1]) 


    chart_data = transformForChart(timeline_data, matchid)

    return chart_data

def transformForChart(timeline_data, matchid):
    # Determine game duration from how many minutes we collected data about gold
    gameDuration = len(timeline_data[1]["totalGold"])
    values = ["totalGold", "minionsKilled", "damageToChamps"]

    all_data = {
        "totalGold": [],
        "minionsKilled": [],
        "damageToChamps": []
    }
    
    for minute in range(gameDuration):
        for value in values:
            minute_data = {"minute": minute}

            for index in range(1, 11):
                player_data = timeline_data[index]
                
                # store each of the desired chart values
                championName = participant_data[matchid][index- 1]["championName"]
                minute_data[championName] = player_data[value][minute]
            
            all_data[value].append(minute_data)

        

    return all_data
        



#test_matchid = "NA1_5233647486"
#process_timeline(test_matchid, "americas")