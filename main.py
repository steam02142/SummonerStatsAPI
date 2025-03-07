from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from riot_api.riot_client import get_player_puuid, process_matches, get_profile_icon
from riot_api.timeline import process_timeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

@app.get("/puuid")
def fetch_puuid(riot_id, tagline, region):
    try:
        puuid = get_player_puuid(riot_id, tagline, region)

        return {
            "puuid": puuid,
            "id": riot_id,
            "tagline": tagline
        }
    except Exception as e:
        return {
            "error": str(e),
            "id": riot_id,
            "tagline": tagline
        }


@app.get("/matches")
def fetch_matches(puuid, num_matches, region):
    return process_matches(puuid, num_matches, region)

@app.get("/timeline")
def fetch_timeline(matchid, region):
    return process_timeline(matchid, region)

@app.get("/profileIcon")
def fetch_profile_icon(puuid):
    return get_profile_icon(puuid, "na1")