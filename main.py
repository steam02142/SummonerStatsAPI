from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from riot_api.riot_client import get_player_puuid

riot_id = "wumpus"
tagline = "1112"

#puuid = get_player_puuid(riot_id, tagline)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

@app.get("/puuid")
def fetch_puuid(riot_id: str, tagline: str):
    try:
        puuid = get_player_puuid(riot_id, tagline)

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