from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import requests
import logging
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import re
from datetime import datetime

# --- Load environment variables ---
load_dotenv()
os.environ['GEMINI_API_KEY'] = os.getenv("GEMINI_API_KEY")

# --- Server-Side Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Pydantic Models for Structured AI Agent Communication ---
class PokemonData(BaseModel):
    """Structured Pokemon data for AI agents"""
    name: str
    id: int
    height: float
    weight: float
    abilities: List[str]
    types: List[str]
    stats: Dict[str, int]
    sprite: Optional[str]
    description: Optional[str] = None
    battle_effectiveness: Optional[Dict[str, Any]] = None


class TeamMember(BaseModel):
    """Enhanced team member with strategic data"""
    name: str
    primary_type: str
    secondary_type: Optional[str] = None
    role: str
    reasoning: str
    suggested_moves: Optional[List[str]] = None
    stats: Optional[Dict[str, int]] = None
    sprite: Optional[str] = None


class TeamRequest(BaseModel):
    """Request model for team generation"""
    description: str = Field(..., description="Natural language description of desired team")
    include_stats: bool = Field(default=True, description="Include Pokemon stats from PokeAPI")
    max_retries: int = Field(default=3, description="Max retries for invalid Pokemon names")


class CounterPokemon(BaseModel):
    """Counter Pokemon suggestion"""
    name: str
    type: str
    reason: str
    sprite: Optional[str] = None


class BattleResult(BaseModel):
    """Head to head battle result"""
    winner: str
    confidence: str
    reasoning: str
    key_factors: List[str]


class MCPResponse(BaseModel):
    """Standard MCP response wrapper"""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    timestamp: str
    agent_instructions: Optional[str] = None


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Pokémon MCP Server - AI Agent Middleware",
    description="Modular Control Platform providing strategic Pokémon data abstractions for AI agents. Combines PokeAPI factual data with AI-powered strategic analysis.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PokeAPI Configuration ---
BASE_URL = "https://pokeapi.co/api/v2/"
REQUEST_TIMEOUT = 10

# --- Initialize LLM ---
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7
)

# --- Prompt Templates ---
description_prompt = PromptTemplate(
    input_variables=["name", "types", "abilities", "stats"],
    template="""
    You are a Pokemon expert. Provide a detailed and engaging description for {name}.

    Pokemon Details:
    - Types: {types}
    - Abilities: {abilities}
    - Base Stats: {stats}

    Write a 2-3 sentence description that includes:
    1. What this Pokemon looks like or represents
    2. Its key characteristics or personality
    3. What makes it special in battle or as a companion

    Keep it informative but engaging, suitable for trainers who want to know more about this Pokemon.
    """
)

battle_prompt = PromptTemplate(
    input_variables=["pokemon1_name", "pokemon1_types", "pokemon1_stats", "pokemon2_name", "pokemon2_types",
                     "pokemon2_stats"],
    template="""
    You are a Pokemon battle expert. Analyze this head-to-head matchup and determine who would likely win.

    Pokemon 1: {pokemon1_name}
    Types: {pokemon1_types}
    Stats: {pokemon1_stats}

    Pokemon 2: {pokemon2_name} 
    Types: {pokemon2_types}
    Stats: {pokemon2_stats}

    Consider:
    - Type effectiveness and weaknesses
    - Base stat comparison (especially Attack, Defense, Speed)
    - Overall battle potential

    Respond with:
    Winner: [Pokemon Name]
    Confidence: [High/Medium/Low]
    Reasoning: [2-3 sentence explanation of why this Pokemon would win]
    Key Factors: [List 2-3 main factors that determine the outcome]

    Format your response exactly as shown above.
    """
)

counter_prompt = PromptTemplate(
    input_variables=["target_pokemon", "target_types", "target_stats"],
    template="""
    You are a Pokemon strategy expert. Suggest 3-4 Pokemon that would be effective counters against {target_pokemon}.

    Target Pokemon Details:
    - Types: {target_types}
    - Base Stats: {target_stats}

    For each counter Pokemon, provide:
    - Name: [Exact Pokemon name]
    - Type: [Primary type, or Primary/Secondary if dual-type]
    - Reason: [Brief explanation of why it's an effective counter]

    Focus on:
    - Type advantages
    - Stat advantages
    - Common strategies that work well

    Format each suggestion as:
    Name: [Pokemon Name]
    Type: [Type(s)]
    Reason: [One sentence explanation]

    Separate each Pokemon with a line break.
    """
)

team_analysis_prompt = PromptTemplate(
    input_variables=["description", "team_members"],
    template="""
    You are a Pokemon team strategy expert. Analyze why this team is well-suited for the user's request.

    User Request: {description}

    Generated Team: {team_members}

    Provide a detailed analysis explaining:
    1. How this team addresses the user's specific requirements
    2. The strategic synergy between team members
    3. Type coverage and balance
    4. Strengths and potential weaknesses
    5. Overall team effectiveness

    Write 3-4 sentences that explain why this team composition is excellent for the user's needs.
    Focus on strategy, synergy, and how it fulfills their request.
    """
)

# --- LLM Chains ---
description_chain = LLMChain(llm=llm, prompt=description_prompt)
battle_chain = LLMChain(llm=llm, prompt=battle_prompt)
counter_chain = LLMChain(llm=llm, prompt=counter_prompt)
team_analysis_chain = LLMChain(llm=llm, prompt=team_analysis_prompt)


# --- Enhanced Data Abstraction Layer ---
class PokemonDataAbstractor:
    """Abstracts and enriches PokeAPI data for AI agents"""

    @staticmethod
    async def fetch_enhanced_pokemon_data(name: str, include_description: bool = True) -> PokemonData:
        """Fetch and enhance Pokemon data with AI-generated description"""
        try:
            # Get base data from PokeAPI
            base_data = await PokemonDataAbstractor._fetch_base_pokemon_data(name)

            # Add AI-generated description if requested
            if include_description:
                try:
                    description_response = description_chain.run(
                        name=base_data.name,
                        types=", ".join(base_data.types),
                        abilities=", ".join(base_data.abilities),
                        stats=base_data.stats
                    )
                    base_data.description = description_response.strip()
                except Exception as e:
                    logger.warning(f"Failed to generate description for {name}: {e}")
                    base_data.description = f"{base_data.name} is a {'/'.join(base_data.types)} type Pokemon."

            return base_data

        except Exception as e:
            logger.error(f"Failed to fetch enhanced data for {name}: {e}")
            raise HTTPException(status_code=500, detail=f"Data retrieval failed: {e}")

    @staticmethod
    async def _fetch_base_pokemon_data(name: str) -> PokemonData:
        """Fetch base Pokemon data from PokeAPI"""
        if not name or not name.strip():
            raise HTTPException(status_code=400, detail="Pokemon name cannot be empty")

        pokemon_name = name.lower().strip()
        url = f"{BASE_URL}pokemon/{pokemon_name}"

        try:
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            return PokemonData(
                name=data["name"].capitalize(),
                id=data["id"],
                height=data["height"] / 10,  # Convert to meters
                weight=data["weight"] / 10,  # Convert to kg
                abilities=[
                    ability["ability"]["name"].replace("-", " ").title()
                    for ability in data["abilities"]
                ],
                types=[
                    pok_type["type"]["name"].capitalize()
                    for pok_type in data["types"]
                ],
                stats={
                    stat["stat"]["name"].replace("-", " ").title(): stat["base_stat"]
                    for stat in data["stats"]
                },
                sprite=data["sprites"]["front_default"]
            )

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Pokemon '{name}' not found")
            raise HTTPException(status_code=response.status_code, detail=f"PokeAPI error: {e}")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"Network error: {e}")


# --- MCP Response Helper ---
def create_mcp_response(success: bool, data: Any, agent_instructions: str = None) -> MCPResponse:
    """Create standardized MCP response for AI agents"""
    return MCPResponse(
        success=success,
        data=data,
        metadata={
            "server_version": "2.0.0",
            "data_source": "PokeAPI + AI Strategic Analysis",
            "capabilities": ["pokemon_data", "ai_descriptions", "battle_analysis", "counter_suggestions"]
        },
        timestamp=datetime.now().isoformat(),
        agent_instructions=agent_instructions
    )


# --- Enhanced MCP Endpoints ---

@app.get("/", summary="MCP Server Information")
async def mcp_info():
    """Information about this MCP server for AI agents"""
    return create_mcp_response(
        success=True,
        data={
            "server_type": "Pokemon Strategic Analysis MCP",
            "purpose": "Middleware for AI agents to access strategic Pokemon data",
            "capabilities": [
                "Enhanced Pokemon data retrieval with AI descriptions",
                "Head-to-head battle analysis",
                "Counter Pokemon suggestions",
                "Strategic comparison analysis"
            ],
            "endpoints": {
                "pokemon_data": "/pokemon/{name}",
                "pokemon_comparison": "/compare/{pokemon1}/{pokemon2}",
                "battle_analysis": "/battle/{pokemon1}/{pokemon2}",
                "counter_suggestions": "/counters/{pokemon_name}"
            }
        },
        agent_instructions="Use these endpoints to access Pokemon data with AI-enhanced features"
    )


# --- Main Endpoints ---

@app.get("/pokemon/{name}")
async def get_pokemon_details(name: str):
    """Get Pokemon details with AI-generated description"""
    try:
        pokemon_data = await PokemonDataAbstractor.fetch_enhanced_pokemon_data(name, True)
        return pokemon_data.dict()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare/{pokemon1_name}/{pokemon2_name}")
async def compare_pokemon_details(pokemon1_name: str, pokemon2_name: str):
    """Compare two Pokemon with basic data"""
    try:
        pok1_data = await PokemonDataAbstractor.fetch_enhanced_pokemon_data(pokemon1_name, True)
        pok2_data = await PokemonDataAbstractor.fetch_enhanced_pokemon_data(pokemon2_name, True)
        return {"pokemon1": pok1_data.dict(), "pokemon2": pok2_data.dict()}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/battle/{pokemon1_name}/{pokemon2_name}")
async def head_to_head_battle(pokemon1_name: str, pokemon2_name: str):
    """Analyze head-to-head battle between two Pokemon"""
    try:
        # Fetch Pokemon data
        pok1_data = await PokemonDataAbstractor._fetch_base_pokemon_data(pokemon1_name)
        pok2_data = await PokemonDataAbstractor._fetch_base_pokemon_data(pokemon2_name)

        # Generate battle analysis
        battle_response = battle_chain.run(
            pokemon1_name=pok1_data.name,
            pokemon1_types=", ".join(pok1_data.types),
            pokemon1_stats=pok1_data.stats,
            pokemon2_name=pok2_data.name,
            pokemon2_types=", ".join(pok2_data.types),
            pokemon2_stats=pok2_data.stats
        )

        # Parse the response
        lines = battle_response.strip().split('\n')
        winner = ""
        confidence = ""
        reasoning = ""
        key_factors = []

        for line in lines:
            line = line.strip()
            if line.startswith("Winner:"):
                winner = line.split(":", 1)[1].strip()
            elif line.startswith("Confidence:"):
                confidence = line.split(":", 1)[1].strip()
            elif line.startswith("Reasoning:"):
                reasoning = line.split(":", 1)[1].strip()
            elif line.startswith("Key Factors:"):
                factors_text = line.split(":", 1)[1].strip()
                # Simple parsing - split by common separators
                key_factors = [f.strip() for f in factors_text.replace("-", "").split(",") if f.strip()]

        battle_result = BattleResult(
            winner=winner or "Unknown",
            confidence=confidence or "Medium",
            reasoning=reasoning or "Analysis unavailable",
            key_factors=key_factors or ["Type matchup", "Stat comparison"]
        )

        return {
            "pokemon1": pok1_data.dict(),
            "pokemon2": pok2_data.dict(),
            "battle_result": battle_result.dict()
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Battle analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/counters/{pokemon_name}")
async def suggest_counters(pokemon_name: str):
    """Suggest counter Pokemon for the given Pokemon"""
    try:
        # Fetch target Pokemon data
        target_data = await PokemonDataAbstractor._fetch_base_pokemon_data(pokemon_name)

        # Generate counter suggestions
        counter_response = counter_chain.run(
            target_pokemon=target_data.name,
            target_types=", ".join(target_data.types),
            target_stats=target_data.stats
        )

        # Parse the response
        counters = []
        current_counter = {}

        for line in counter_response.strip().split('\n'):
            line = line.strip()
            if not line:
                if current_counter:
                    # Fetch sprite for counter Pokemon
                    try:
                        counter_data = await PokemonDataAbstractor._fetch_base_pokemon_data(current_counter["name"])
                        current_counter["sprite"] = counter_data.sprite
                    except:
                        current_counter["sprite"] = None

                    counters.append(CounterPokemon(**current_counter))
                    current_counter = {}
                continue

            if line.startswith("Name:"):
                current_counter["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("Type:"):
                current_counter["type"] = line.split(":", 1)[1].strip()
            elif line.startswith("Reason:"):
                current_counter["reason"] = line.split(":", 1)[1].strip()

        # Add the last counter if exists
        if current_counter:
            try:
                counter_data = await PokemonDataAbstractor._fetch_base_pokemon_data(current_counter["name"])
                current_counter["sprite"] = counter_data.sprite
            except:
                current_counter["sprite"] = None
            counters.append(CounterPokemon(**current_counter))

        return {
            "target_pokemon": target_data.dict(),
            "counters": [counter.dict() for counter in counters]
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Counter suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/team/generate")
async def generate_team(description: str = Query(..., description="Team description")):
    """Generate a Pokemon team based on description with AI analysis"""
    try:
        # Simple team generation using LLM
        team_prompt_template = PromptTemplate(
            input_variables=["description"],
            template="""
            Generate a Pokemon team of 6 Pokemon based on this description: {description}

            For each Pokemon, provide:
            - name: [Exact Pokemon name]
            - type: [Primary type]
            - role: [Role in team like Attacker, Tank, Support, etc.]

            Format each Pokemon as:
            Name: [Pokemon Name]
            Type: [Type]
            Role: [Role]

            Separate each Pokemon with a line break.
            """
        )

        team_chain = LLMChain(llm=llm, prompt=team_prompt_template)
        team_response = team_chain.run(description=description)

        # Parse team response
        team = []
        current_member = {}

        for line in team_response.strip().split('\n'):
            line = line.strip()
            if not line:
                if current_member:
                    # Fetch sprite and additional data for team member
                    try:
                        member_data = await PokemonDataAbstractor._fetch_base_pokemon_data(current_member["name"])
                        current_member["sprite"] = member_data.sprite
                        current_member["stats"] = member_data.stats
                        current_member["types"] = member_data.types
                    except:
                        current_member["sprite"] = None
                        current_member["stats"] = {}
                        current_member["types"] = [current_member.get("type", "Unknown")]

                    team.append(current_member)
                    current_member = {}
                continue

            if line.startswith("Name:"):
                current_member["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("Type:"):
                current_member["type"] = line.split(":", 1)[1].strip()
            elif line.startswith("Role:"):
                current_member["role"] = line.split(":", 1)[1].strip()

        # Add the last member if exists
        if current_member:
            try:
                member_data = await PokemonDataAbstractor._fetch_base_pokemon_data(current_member["name"])
                current_member["sprite"] = member_data.sprite
                current_member["stats"] = member_data.stats
                current_member["types"] = member_data.types
            except:
                current_member["sprite"] = None
                current_member["stats"] = {}
                current_member["types"] = [current_member.get("type", "Unknown")]
            team.append(current_member)

        # Generate team analysis
        team_members_str = ", ".join([f"{member['name']} ({member['role']})" for member in team])

        try:
            analysis = team_analysis_chain.run(
                description=description,
                team_members=team_members_str
            )
        except Exception as e:
            logger.warning(f"Failed to generate team analysis: {e}")
            analysis = "This team provides a balanced combination of Pokemon that work well together to achieve your strategic goals."

        return {
            "team": team,
            "analysis": analysis,
            "description": description
        }

    except Exception as e:
        logger.error(f"Team generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Health Check ---
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return create_mcp_response(
        success=True,
        data={"status": "healthy", "services": ["PokeAPI", "Gemini AI", "LLM Chains"]},
        agent_instructions="All systems operational"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)