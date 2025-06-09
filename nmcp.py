from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

import json
import re

# --- Load environment variables ---
load_dotenv()
os.environ['GEMINI_API_KEY'] = os.getenv("GEMINI_API_KEY")

# --- Server-Side Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Pokémon MCP - Core Data Services",
    description="Provides basic Pokémon information retrieval, comparison, and team generation via PokeAPI and Gemini.",
    version="1.1.0"
)

# --- CORS Configuration ---
origins = [
    "http://localhost:8501",  # Streamlit frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PokeAPI Base URL ---
BASE_URL = "https://pokeapi.co/api/v2/"

# --- Helper: Fetch Pokémon Data ---
def _fetch_pokemon_data_from_pokeapi(name: str):
    if not name:
        logger.warning("Attempted to fetch Pokémon with empty name.")
        raise HTTPException(status_code=400, detail="Pokémon name cannot be empty.")

    pokemon_name = name.lower()
    url = f"{BASE_URL}pokemon/{pokemon_name}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        pok_data = response.json()

        pokemon_details = {
            "name": pok_data["name"].capitalize(),
            "id": pok_data["id"],
            "height": pok_data["height"] / 10,
            "weight": pok_data["weight"] / 10,
            "abilities": [
                ability["ability"]["name"].replace("-", " ").title()
                for ability in pok_data["abilities"]
            ],
            "types": [
                pok_type["type"]["name"].capitalize()
                for pok_type in pok_data["types"]
            ],
            "stats": {
                stat["stat"]["name"].replace("-", " ").title(): stat["base_stat"]
                for stat in pok_data["stats"]
            },
            "sprite": pok_data["sprites"]["front_default"]
        }
        logger.info(f"Successfully fetched data for {name}")
        return pokemon_details
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            logger.warning(f"Pokémon '{name}' not found (404).")
            raise HTTPException(status_code=404, detail=f"Pokémon '{name}' not found. Please check the spelling.")
        else:
            logger.error(f"HTTP Error fetching data for {name}: {e}")
            raise HTTPException(status_code=response.status_code, detail=f"HTTP Error: {e}")
    except requests.exceptions.ConnectionError:
        logger.error("Connection Error to PokeAPI.")
        raise HTTPException(status_code=503, detail="Connection Error: Could not reach PokeAPI. Please check server's internet connection.")
    except requests.exceptions.Timeout:
        logger.error("Timeout Error from PokeAPI.")
        raise HTTPException(status_code=504, detail="Timeout Error: PokeAPI took too long to respond.")
    except requests.exceptions.RequestException as e:
        logger.error(f"An unexpected RequestException occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during API request: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred while processing data for {name}.")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

# --- Endpoints ---

@app.get("/pokemon/{name}", summary="Retrieve detailed information for a single Pokémon")
async def get_pokemon_details(name: str):
    return _fetch_pokemon_data_from_pokeapi(name)

@app.get("/compare/{pokemon1_name}/{pokemon2_name}", summary="Compare attributes of two Pokémon")
async def compare_pokemon_details(pokemon1_name: str, pokemon2_name: str):
    logger.info(f"Received comparison request for {pokemon1_name} and {pokemon2_name}")
    pok1_info = _fetch_pokemon_data_from_pokeapi(pokemon1_name)
    pok2_info = _fetch_pokemon_data_from_pokeapi(pokemon2_name)
    return {"pokemon1": pok1_info, "pokemon2": pok2_info}

@app.post("/team/generate", summary="Generate a Pokémon team from a natural language description")
async def generate_team(description: str):
    try:
        prompt = (
            "You are a Pokémon team-building expert. "
            "Given this team description: '{}', "
            "suggest a team of 6 Pokémon with type and role diversity. "
            "Also write why this team is considered"
            "Format: JSON list with each Pokémon's name, main type, and suggested role."
        ).format(description)

        chat = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )


        response = chat.invoke([HumanMessage(content=prompt)])
        raw_text = response.content

        # extract JSON from the response
        try:
            team = json.loads(raw_text)
        except Exception:
            match = re.search(r"\[.*\]", raw_text, re.DOTALL)
            if match:
                team = json.loads(match.group(0))
            else:
                raise ValueError("Could not parse team from Gemini response.")

        return {"team": team}

    except Exception as e:
        logger.error(f"Team generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Team generation error: {e}")



@app.get("/counters/{pokemon_name}", summary="Suggest counters for a given Pokémon using Gemini")
async def suggest_counters(pokemon_name: str):
    try:
        prompt = (
            f"You are a Pokémon battle strategist. "
            f"Suggest 5 strong counter Pokémon against '{pokemon_name}'. "
            f"For each, provide the Pokémon's name, main type, and a brief reason why it is a good counter. "
            f"Format: JSON list with name, type, reason."
        )

        chat = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # or "gemini-2.0-pro" if you have access
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )

        response = chat.invoke([HumanMessage(content=prompt)])
        raw_text = response.content

        # Try to extract JSON from the response
        try:
            counters = json.loads(raw_text)
        except Exception:
            match = re.search(r"\[.*\]", raw_text, re.DOTALL)
            if match:
                counters = json.loads(match.group(0))
            else:
                raise ValueError("Could not parse counters from Gemini response.")

        return {"counters": counters}

    except Exception as e:
        logger.error(f"Counter suggestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Counter suggestion error: {e}")