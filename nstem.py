import streamlit as st
import requests
import time
from typing import Dict, Any, List

st.set_page_config(
    page_title="Pokémon MCP Server",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Pokémon Game Theme
st.markdown("""
<style>
    /* Import Pokémon-style fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

    /* Global game-style background */
    .main {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 25%, #1e3c72 50%, #2a5298 75%, #1e3c72 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
        position: relative;
    }

    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 25%, #1e3c72 50%, #2a5298 75%, #1e3c72 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }

    /* Animated background */
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Pokémon-style header */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(145deg, #FFD700 0%, #FFA500 50%, #FF6347 100%);
        border-radius: 25px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 2px 8px rgba(255, 255, 255, 0.3),
            0 0 20px rgba(255, 215, 0, 0.5);
        border: 3px solid #FF4500;
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        animation: shine 3s infinite;
    }

    @keyframes shine {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 3.5rem;
        font-weight: 900;
        color: #000080;
        text-shadow: 
            3px 3px 0 #FFFFFF,
            -1px -1px 0 #FFFFFF,
            1px -1px 0 #FFFFFF,
            -1px 1px 0 #FFFFFF,
            0 0 20px rgba(255, 215, 0, 0.8);
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }

    .main-subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.3rem;
        color: #000080;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.8);
        position: relative;
        z-index: 1;
    }

    /* Pokémon game-style cards */
    .feature-card {
        background: linear-gradient(145deg, #4169E1 0%, #6495ED 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 2px 8px rgba(255, 255, 255, 0.2);
        border: 3px solid #FFD700;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }

    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 
            0 16px 48px rgba(0, 0, 0, 0.5),
            inset 0 2px 8px rgba(255, 255, 255, 0.3),
            0 0 30px rgba(255, 215, 0, 0.6);
    }

    .feature-card:hover::before {
        left: 100%;
    }

    .card-header {
        font-family: 'Orbitron', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFD700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Pokémon card styling */
    .pokemon-card {
        background: linear-gradient(145deg, #FFFFFF 0%, #F0F8FF 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 2px 8px rgba(65, 105, 225, 0.1);
        border: 3px solid #4169E1;
        color: #000080;
        font-family: 'Rajdhani', sans-serif;
        position: relative;
    }

    .pokemon-card::after {
        content: '';
        position: absolute;
        top: 10px;
        right: 10px;
        width: 30px;
        height: 30px;
        background: radial-gradient(circle, #FFD700 0%, #FFA500 100%);
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }

    .pokemon-name {
        font-family: 'Orbitron', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: #FF4500;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .pokemon-stat {
        background: linear-gradient(145deg, #4169E1, #6495ED);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        margin: 0.3rem;
        display: inline-block;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border: 2px solid #FFD700;
    }

    /* Pokémon type badges */
    .type-badge {
        padding: 0.4rem 1rem;
        border-radius: 25px;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.5);
    }

    /* Type-specific colors */
    .type-normal { background: linear-gradient(145deg, #A8A878, #C5C5A7); color: #000; }
    .type-fire { background: linear-gradient(145deg, #F08030, #FF6347); color: #FFF; }
    .type-water { background: linear-gradient(145deg, #6890F0, #4682B4); color: #FFF; }
    .type-electric { background: linear-gradient(145deg, #F8D030, #FFD700); color: #000; }
    .type-grass { background: linear-gradient(145deg, #78C850, #90EE90); color: #000; }
    .type-ice { background: linear-gradient(145deg, #98D8D8, #B0E0E6); color: #000; }
    .type-fighting { background: linear-gradient(145deg, #C03028, #DC143C); color: #FFF; }
    .type-poison { background: linear-gradient(145deg, #A040A0, #BA55D3); color: #FFF; }
    .type-ground { background: linear-gradient(145deg, #E0C068, #DEB887); color: #000; }
    .type-flying { background: linear-gradient(145deg, #A890F0, #9370DB); color: #FFF; }
    .type-psychic { background: linear-gradient(145deg, #F85888, #FF69B4); color: #FFF; }
    .type-bug { background: linear-gradient(145deg, #A8B820, #9ACD32); color: #000; }
    .type-rock { background: linear-gradient(145deg, #B8A038, #CD853F); color: #FFF; }
    .type-ghost { background: linear-gradient(145deg, #705898, #8A2BE2); color: #FFF; }
    .type-dragon { background: linear-gradient(145deg, #7038F8, #8B00FF); color: #FFF; }
    .type-dark { background: linear-gradient(145deg, #705848, #2F4F4F); color: #FFF; }
    .type-steel { background: linear-gradient(145deg, #B8B8D0, #C0C0C0); color: #000; }
    .type-fairy { background: linear-gradient(145deg, #EE99AC, #FFB6C1); color: #000; }

    /* Game-style buttons */
    .stButton > button {
        background: linear-gradient(145deg, #FFD700 0%, #FFA500 50%, #FF6347 100%) !important;
        color: #000080 !important;
        border: 3px solid #FF4500 !important;
        border-radius: 25px !important;
        font-family: 'Orbitron', monospace !important;
        font-weight: 700 !important;
        padding: 1rem 2rem !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
        box-shadow: 
            0 6px 20px rgba(0, 0, 0, 0.3),
            inset 0 2px 8px rgba(255, 255, 255, 0.3) !important;
        text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5) !important;
    }

    .stButton > button:hover {
        transform: translateY(-4px) !important;
        box-shadow: 
            0 12px 35px rgba(0, 0, 0, 0.4),
            inset 0 2px 8px rgba(255, 255, 255, 0.4),
            0 0 25px rgba(255, 215, 0, 0.8) !important;
        background: linear-gradient(145deg, #FFA500 0%, #FFD700 50%, #FF6347 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(-2px) !important;
    }

    /* Game-style inputs */
    .stTextInput > div > div > input {
        background: linear-gradient(145deg, #F0F8FF, #FFFFFF) !important;
        border: 3px solid #4169E1 !important;
        border-radius: 15px !important;
        color: #000080 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 
            inset 0 2px 8px rgba(65, 105, 225, 0.1),
            0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #FFD700 !important;
        box-shadow: 
            inset 0 2px 8px rgba(255, 215, 0, 0.2),
            0 0 20px rgba(255, 215, 0, 0.5) !important;
    }

    .stTextArea > div > div > textarea {
        background: linear-gradient(145deg, #F0F8FF, #FFFFFF) !important;
        border: 3px solid #4169E1 !important;
        border-radius: 15px !important;
        color: #000080 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 
            inset 0 2px 8px rgba(65, 105, 225, 0.1),
            0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }

    /* Pokéball loading animation */
    .loading-pokeball {
        width: 60px;
        height: 60px;
        background: 
            linear-gradient(0deg, #FF0000 0%, #FF0000 45%, #000000 45%, #000000 55%, #FFFFFF 55%, #FFFFFF 100%);
        border-radius: 50%;
        border: 4px solid #333;
        position: relative;
        animation: pokeball-spin 2s linear infinite;
        margin: 20px auto;
        box-shadow: 
            0 0 20px rgba(255, 0, 0, 0.5),
            inset 0 0 20px rgba(255, 255, 255, 0.2);
    }

    .loading-pokeball::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        background: linear-gradient(145deg, #FFFFFF, #E0E0E0);
        border-radius: 50%;
        border: 3px solid #333;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    @keyframes pokeball-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Battle result styling */
    .battle-winner {
        background: linear-gradient(145deg, #FFD700 0%, #FFA500 100%);
        color: #000080;
        padding: 1.5rem;
        border-radius: 20px;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        text-align: center;
        margin: 1rem 0;
        font-size: 1.3rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 2px 8px rgba(255, 255, 255, 0.3),
            0 0 30px rgba(255, 215, 0, 0.8);
        border: 3px solid #FF4500;
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.5);
    }

    .team-member {
        background: linear-gradient(145deg, #F0F8FF 0%, #FFFFFF 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 3px solid #4169E1;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.2),
            inset 0 2px 8px rgba(65, 105, 225, 0.1);
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: transform 0.3s ease;
    }

    .team-member:hover {
        transform: translateX(10px);
        box-shadow: 
            0 12px 48px rgba(0, 0, 0, 0.3),
            inset 0 2px 8px rgba(65, 105, 225, 0.2),
            0 0 20px rgba(255, 215, 0, 0.4);
    }

    /* Pokémon tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(145deg, #4169E1, #6495ED);
        border-radius: 25px;
        padding: 8px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #FFD700, #FFA500);
        color: #000080;
        border-radius: 20px;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        border: 2px solid #FF4500;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(145deg, #FFA500, #FFD700);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(145deg, #FF6347, #FF4500);
        color: #FFFFFF;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .feature-card {
            padding: 1rem;
        }
        .pokemon-card {
            padding: 1rem;
        }
    }

    /* Status messages */
    .stSuccess {
        background: linear-gradient(145deg, #90EE90, #98FB98) !important;
        border: 3px solid #32CD32 !important;
        border-radius: 15px !important;
        color: #006400 !important;
        font-weight: 600 !important;
    }

    .stError {
        background: linear-gradient(145deg, #FFB6C1, #FFA0B4) !important;
        border: 3px solid #DC143C !important;
        border-radius: 15px !important;
        color: #8B0000 !important;
        font-weight: 600 !important;
    }

    .stWarning {
        background: linear-gradient(145deg, #FFFFE0, #FFFACD) !important;
        border: 3px solid #FFD700 !important;
        border-radius: 15px !important;
        color: #FF8C00 !important;
        font-weight: 600 !important;
    }

    .stInfo {
        background: linear-gradient(145deg, #E6F3FF, #CCE7FF) !important;
        border: 3px solid #4169E1 !important;
        border-radius: 15px !important;
        color: #000080 !important;
        font-weight: 600 !important;
    }

    /* Game-style progress bars */
    .stat-bar {
        background: linear-gradient(145deg, #E0E0E0, #F5F5F5);
        border-radius: 25px;
        height: 12px;
        margin: 0.3rem 0;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
        border: 2px solid #4169E1;
        overflow: hidden;
    }

    .stat-fill {
        height: 100%;
        background: linear-gradient(90deg, #32CD32 0%, #FFD700 50%, #FF6347 100%);
        border-radius: 25px;
        transition: width 0.8s ease;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

MCP_SERVER_URL = "https://pokemon-mcp-server.onrender.com"


def create_loading_animation():
    """Create a Pokéball loading animation placeholder"""
    return st.empty()


def get_type_class(pokemon_type):
    """Get CSS class for Pokémon type"""
    return f"type-{pokemon_type.lower()}"


def display_pokemon_card(pokemon_data: Dict[str, Any], title: str = None):
    """Display Pokémon info in game style"""
    if not pokemon_data:
        st.warning("No Pokémon data to display.")
        return

    with st.container():
        st.markdown(f"""
        <div class="pokemon-card">
            <div class="pokemon-name">
                {'🎯 ' + title if title else ''} {pokemon_data.get('name', 'Unknown')}
                <span style="color: #4169E1;">(#{pokemon_data.get('id', 'Unknown')})</span>
            </div>
        """, unsafe_allow_html=True)

        # Create columns for image and basic info
        col1, col2 = st.columns([1, 2])

        with col1:
            if pokemon_data.get('sprite'):
                st.image(pokemon_data['sprite'], width=220)

        with col2:
            # Types with proper styling
            types = pokemon_data.get('types', [])
            if types:
                types_html = ''.join([f'<span class="type-badge {get_type_class(t)}">{t}</span>' for t in types])
                st.markdown(f"**Types:** {types_html}", unsafe_allow_html=True)

            # Basic stats
            height = pokemon_data.get('height', 'Unknown')
            weight = pokemon_data.get('weight', 'Unknown')
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <span class="pokemon-stat">📏 HEIGHT: {height}m</span>
                <span class="pokemon-stat">⚖️ WEIGHT: {weight}kg</span>
            </div>
            """, unsafe_allow_html=True)

            # Abilities
            abilities = pokemon_data.get('abilities', [])
            if abilities:
                abilities_html = ''.join([f'<span class="pokemon-stat">✨ {a.upper()}</span>' for a in abilities])
                st.markdown(f"**Abilities:** {abilities_html}", unsafe_allow_html=True)

        # Description
        if pokemon_data.get('description'):
            st.markdown(f"""
            <div style="margin: 1rem 0; padding: 1.5rem; background: linear-gradient(145deg, #E6F3FF, #CCE7FF); border-radius: 15px; border: 3px solid #4169E1; color: #000080;">
                <strong style="color: #FF4500;">🔍 TRAINER ANALYSIS:</strong><br>
                <span style="font-family: 'Rajdhani', sans-serif; font-weight: 600; line-height: 1.5;">{pokemon_data['description']}</span>
            </div>
            """, unsafe_allow_html=True)

        # Base Stats with game-style bars
        stats = pokemon_data.get('stats', {})
        if stats:
            st.markdown("**📊 BASE STATS:**")
            for stat, value in stats.items():
                percentage = min(int(value) / 200 * 100, 100)
                st.markdown(f"""
                <div style="margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem;">
                        <span style="color: #FF4500; font-weight: 700; font-family: 'Orbitron', monospace;">{stat.upper()}:</span>
                        <span style="color: #000080; font-weight: 700; font-family: 'Orbitron', monospace;">{value}</span>
                    </div>
                    <div class="stat-bar">
                        <div class="stat-fill" style="width: {percentage}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


def make_api_request(url: str, method: str = "GET", **kwargs):
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, timeout=30, **kwargs)

        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None, "Pokémon not found. Please check the spelling and try again."
        else:
            error_detail = e.response.json().get('detail',
                                                 'An unexpected error occurred.') if e.response.text else 'Server error occurred.'
            return None, f"Server Error: {error_detail}"
    except requests.exceptions.ConnectionError:
        return None, "🔌 Could not connect to the MCP server. Please ensure it's running on localhost:8000"
    except requests.exceptions.Timeout:
        return None, "⏱️ Request timed out. The server might be busy, please try again."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


# Game-style Header
st.markdown("""
<div class="main-header">
    <div class="main-title">⚡ POKÉMON BATTLE CENTER ⚡</div>
    <div class="main-subtitle">
        🚀 POWERED BY AI • ⚡ REAL-TIME DATA • 🎮 GAME EXPERIENCE
    </div>
</div>
""", unsafe_allow_html=True)

# Creating game-style tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 **POKÉDEX**", "⚔️ **BATTLE ARENA**", "🛡️ **STRATEGY LAB**", "🤝 **TEAM BUILDER**"])

with tab1:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">🔍 POKÉDEX SCANNER</div>
        <p style="color: white; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1.1rem;">
            Access comprehensive Pokémon data with advanced AI analysis!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        search_name = st.text_input(
            "",
            key="single_pokemon_search",
            placeholder="🎯 ENTER POKÉMON NAME (e.g., PIKACHU, CHARIZARD, MEWTWO)",
            help="Type any Pokémon name to access detailed information"
        )
    with col2:
        search_button = st.button("🔍 **SCAN**", key="search_button", use_container_width=True)

    if search_button or (search_name and len(search_name) > 2):
        if search_name:
            with st.spinner("🔮 SCANNING POKÉDEX DATABASE..."):
                loading_placeholder = create_loading_animation()
                loading_placeholder.markdown("""
                <div class="loading-pokeball"></div>
                <p style="text-align: center; color: white; font-family: 'Orbitron', monospace; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                    🔮 CATCHING DATA... 🔮
                </p>
                """, unsafe_allow_html=True)

                data, error = make_api_request(f"{MCP_SERVER_URL}/pokemon/{search_name}")

                loading_placeholder.empty()

                if data:
                    display_pokemon_card(data)

                    # Game-style info box
                    st.markdown("""
                    <div style="margin-top: 2rem; padding: 1.5rem; background: linear-gradient(145deg, #4169E1, #6495ED); border-radius: 20px; border: 3px solid #FFD700; color: white;">
                        <h4 style="color: #FFD700; font-family: 'Orbitron', monospace; font-weight: 700;">💡 TRAINER TIPS:</h4>
                        <p style="font-family: 'Rajdhani', sans-serif; font-weight: 600; line-height: 1.6;">
                        • Test this Pokémon's battle potential in the BATTLE ARENA!<br>• Analyze strategic counters in the STRATEGY LAB!<br>
                        • Build the ultimate team in the TEAM BUILDER!
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ {error}")
        else:
            st.warning("⚠️ Please enter a Pokémon name to search.")

with tab2:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">⚔️ BATTLE ARENA</div>
        <p style="color: white; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1.1rem;">
            Compare Pokémon stats and simulate epic battles with advanced AI analysis!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Pokémon Comparison Section
    st.markdown("### 🆚 **POKÉMON BATTLE SIMULATOR**")
    col1, col2 = st.columns(2)

    with col1:
        pokemon1_name = st.text_input(
            "🥊 **RED CORNER FIGHTER**",
            key="pokemon1_input",
            placeholder="e.g., CHARIZARD"
        )
    with col2:
        pokemon2_name = st.text_input(
            "🥊 **BLUE CORNER FIGHTER**",
            key="pokemon2_input",
            placeholder="e.g., BLASTOISE"
        )

    col1, col2 = st.columns([1, 1])
    with col1:
        compare_button = st.button("📊 **ANALYZE FIGHTERS**", key="compare_button", use_container_width=True)
    with col2:
        battle_button_disabled = not (pokemon1_name and pokemon2_name)
        if not battle_button_disabled:
            battle_button = st.button("⚡ **INITIATE BATTLE!**", key="battle_button", use_container_width=True)
        else:
            st.button("⚡ **INITIATE BATTLE!**", key="battle_button_disabled", disabled=True, use_container_width=True,
                      help="Enter both fighter names first")

    if compare_button and pokemon1_name and pokemon2_name:
        with st.spinner("🔥 Analyzing battle data..."):
            # Fixed loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <div class="loading-pokeball"></div>
            <p style="text-align: center; color: white; font-family: 'Orbitron', monospace; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                🔥 ANALYZING FIGHTERS... 🔥
            </p>
            """, unsafe_allow_html=True)

            data, error = make_api_request(f"{MCP_SERVER_URL}/compare/{pokemon1_name}/{pokemon2_name}")

            loading_placeholder.empty()

            if data:
                st.markdown("### 📊 **FIGHTER ANALYSIS**")
                col1, col2 = st.columns(2)

                with col1:
                    display_pokemon_card(data["pokemon1"], "🔴 RED CORNER")
                with col2:
                    display_pokemon_card(data["pokemon2"], "🔵 BLUE CORNER")

                # Store for battle
                st.session_state['comparison_pokemon1'] = pokemon1_name
                st.session_state['comparison_pokemon2'] = pokemon2_name

                st.success("✅ Fighter analysis complete! Ready for epic battle!")
            else:
                st.error(f"❌ {error}")

    # Battle Analysis
    if 'battle_button' in locals() and battle_button:
        with st.spinner("⚡ EPIC BATTLE IN PROGRESS..."):
            # Fixed loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <div class="loading-pokeball"></div>
            <p style="text-align: center; color: white; font-family: 'Orbitron', monospace; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                ⚡ EPIC BATTLE IN PROGRESS... ⚡
            </p>
            """, unsafe_allow_html=True)

            time.sleep(2)  # Add dramatic pause
            data, error = make_api_request(f"{MCP_SERVER_URL}/battle/{pokemon1_name}/{pokemon2_name}")

            loading_placeholder.empty()

            if data:
                battle_result = data.get('battle_result', {})
                winner = battle_result.get('winner', 'Unknown')
                confidence = battle_result.get('confidence', 'Medium')

                st.markdown(f"""
                <div class="battle-winner">
                    🏆 <strong>CHAMPION: {winner.upper()}</strong>
                    <br><small style="font-size: 0.9rem;">Victory Confidence: {confidence}</small>
                </div>
                """, unsafe_allow_html=True)

                # Battle Analysis - Improved contrast
                reasoning = battle_result.get('reasoning', 'No analysis available')
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #2C3E50, #34495E); padding: 1.5rem; border-radius: 20px; margin: 1rem 0; border: 3px solid #FFD700; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <h4 style="color: #FFD700; font-family: 'Orbitron', monospace; font-weight: 700; margin-bottom: 1rem;">🧠 BATTLE TACTICAL ANALYSIS</h4>
                    <p style="font-family: 'Rajdhani', sans-serif; font-weight: 600; line-height: 1.6; color: #FFFFFF; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{reasoning}</p>
                </div>
                """, unsafe_allow_html=True)

                # Key Factors - Improved contrast
                key_factors = battle_result.get('key_factors', [])
                if key_factors:
                    st.markdown("#### 🎯 **KEY VICTORY FACTORS:**")
                    for i, factor in enumerate(key_factors, 1):
                        if factor.strip():
                            st.markdown(f"""
                            <div style="background: linear-gradient(145deg, #27AE60, #2ECC71); padding: 1rem; border-radius: 15px; margin: 0.5rem 0; border: 3px solid #FFD700; color: #FFFFFF; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                                <strong style="font-family: 'Orbitron', monospace; color: #FFD700;">#{i}.</strong> 
                                <span style="font-family: 'Rajdhani', sans-serif; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{factor}</span>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.error(f"❌ {error}")

with tab3:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">🛡️ STRATEGY LAB</div>
        <p style="color: white; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1.1rem;">
            Get AI-powered counter recommendations to dominate your battles!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        counter_pokemon = st.text_input(
            "",
            key="counter_input",
            placeholder="🎯 ENTER TARGET POKÉMON (e.g., GARCHOMP, DRAGONITE)",
            help="Find the ultimate counters for any Pokémon"
        )
    with col2:
        counter_button = st.button("🔍 **ANALYZE WEAKNESSES**", key="suggest_counters_button", use_container_width=True)

    if counter_button and counter_pokemon:
        with st.spinner("🧠 Analyzing battle data and calculating optimal counters..."):
            # Fixed loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <div class="loading-pokeball"></div>
            <p style="text-align: center; color: white; font-family: 'Orbitron', monospace; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                🧠 CALCULATING COUNTERS... 🧠
            </p>
            """, unsafe_allow_html=True)

            data, error = make_api_request(f"{MCP_SERVER_URL}/counters/{counter_pokemon}")

            loading_placeholder.empty()

            if data:
                target_pokemon = data.get('target_pokemon', {})
                counters = data.get('counters', [])

                if target_pokemon:
                    st.markdown("### 🎯 **TARGET ANALYSIS**")
                    display_pokemon_card(target_pokemon)

                if counters:
                    st.markdown("### ⚡ **RECOMMENDED BATTLE COUNTERS**")
                    for i, counter in enumerate(counters, 1):
                        sprite_html = f"<img src='{counter['sprite']}' width='90' style='align-self: center; margin-right: 1rem; border-radius: 10px; border: 2px solid #FFD700;'>" if counter.get(
                            'sprite') else ""
                        details_html = f"""
                        <div style='flex-grow: 1;'>
                            <h4 style="color: #FFD700; margin-bottom: 0.5rem; font-family: 'Orbitron', monospace; font-weight: 700;">
                                #{i} {counter.get('name', 'Unknown')}
                                <span class="type-badge {get_type_class(counter.get('type', ''))}">{counter.get('type', 'Unknown')}</span>
                            </h4>
                            <div style="color: #FFFFFF; line-height: 1.5; font-family: 'Rajdhani', sans-serif; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.7); background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 8px;">
                                <strong style="color: #FF6B6B;">🎯 Strategic Advantage:</strong> {counter.get('reason', 'Tactical superiority')}
                            </div>
                        </div>
                        """
                        st.markdown(f"""
                        <div class="team-member" style="background: linear-gradient(145deg, #2C3E50, #34495E); border: 3px solid #FFD700; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                            {sprite_html}
                            {details_html}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("🤔 No specific counters found in database. Try a different Pokémon!")
            else:
                st.error(f"❌ {error}")

with tab4:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">🤝 TEAM BUILDER</div>
        <p style="color: white; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1.1rem;">
            Create your ultimate dream team with AI-powered strategic analysis!
        </p>
    </div>
    """, unsafe_allow_html=True)

    team_description = st.text_area(
        "🎨 **DESCRIBE YOUR ULTIMATE TEAM STRATEGY:**",
        placeholder="Example: 'A balanced competitive team with devastating offense, one legendary dragon-type, and perfect type coverage for championship tournaments'",
        height=120,
        help="Be specific about your battle strategy - the AI will craft a team based on your vision!"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("✨ **FORGE DREAM TEAM**", key="generate_team_button", use_container_width=True)

    if generate_button and team_description:
        with st.spinner("🎨 AI Master Trainer crafting your ultimate team..."):
            # Fixed loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <div class="loading-pokeball"></div>
            <p style="text-align: center; color: white; font-family: 'Orbitron', monospace; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
                🎨 FORGING DREAM TEAM... 🎨
            </p>
            """, unsafe_allow_html=True)

            time.sleep(2)  # Add anticipation
            data, error = make_api_request(
                f"{MCP_SERVER_URL}/team/generate",
                method="POST",
                params={"description": team_description}
            )

            loading_placeholder.empty()

            if data:
                team = data.get("team", [])

                if team:
                    st.markdown("### 🌟 **YOUR AI-FORGED CHAMPION TEAM**")
                    st.markdown(f"""
                    <div style="background: linear-gradient(145deg, #E67E22, #F39C12); padding: 1.5rem; border-radius: 20px; margin: 1rem 0; border: 3px solid #FFD700; color: #FFFFFF; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                        <strong style="font-family: 'Orbitron', monospace; font-weight: 700; color: #FFFFFF; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">🎯 TEAM STRATEGY BLUEPRINT:</strong> 
                        <br><span style="font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">{team_description}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display team in a nice grid
                    cols = st.columns(2)
                    for i, member in enumerate(team):
                        with cols[i % 2]:
                            sprite_html = f"<img src='{member['sprite']}' width='120' style='border-radius: 10px; border: 3px solid #FFD700; margin: 0.5rem 0;'>" if member.get(
                                'sprite') else ""
                            st.markdown(f"""
                            <div class="team-member" style="background: linear-gradient(145deg, #2C3E50, #34495E); border: 3px solid #FFD700; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                                <div>
                                    <h4 style="color: #FFD700; margin-bottom: 0.5rem; font-family: 'Orbitron', monospace; font-weight: 700;">
                                        #{i + 1} {member.get('name', 'Unknown')}
                                    </h4>
                                    <div style="margin: 0.5rem 0;">
                                        <span class="type-badge {get_type_class(member.get('type', ''))}">{member.get('type', 'Unknown')}</span>
                                    </div>
                                    <div style="color: #FFFFFF; font-family: 'Rajdhani', sans-serif; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.7); background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 8px; margin: 0.5rem 0;">
                                        <strong style="color: #FF6B6B;">🎭 Battle Role:</strong> {member.get('role', 'Elite Team Member')}
                                    </div>
                                    {sprite_html}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("""
                    <div style="background: linear-gradient(145deg, #27AE60, #2ECC71); padding: 1.5rem; border-radius: 20px; margin: 2rem 0; border: 3px solid #FFD700; color: #FFFFFF; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                        <strong style="font-family: 'Orbitron', monospace; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">🎉 CHAMPION TEAM FORGED SUCCESSFULLY!</strong><br>
                        <span style="font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
                        Your team has been strategically crafted with perfect balance and battle synergy in mind.
                        Test these legendary fighters in the BATTLE ARENA for ultimate dominance!
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(
                        "🤔 Couldn't forge a team with that strategy. Try being more specific about your battle vision!")
            else:
                st.error(f"❌ {error}")
    elif generate_button:
        st.warning("⚠️ Please describe your ultimate team strategy first!")

# Epic Footer 
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(145deg, #4169E1, #6495ED); border-radius: 25px; margin: 2rem 0; border: 3px solid #FFD700; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
    <h3 style="color: #FFD700; font-family: 'Orbitron', monospace; font-weight: 700; margin-bottom: 1rem;">
        ⚡ POKÉMON BATTLE CENTER ⚡
    </h3>
    <p style="color: white; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1rem; line-height: 1.5;">
        🏆 Developed with passion by Abuzar Mohammed Makeen<br>
        📊 Battle data powered by PokéAPI • 🧠 AI insights by advanced neural networks<br>
        ⚔️ Ready for championship battles • 🌟 Forge your legacy!
    </p>
    <div style="margin-top: 1rem;">
        <span style="color: #FFD700; font-size: 1.5rem;">🔥 🎮 ⚡ 🏆 ⚔️</span>
    </div>
</div>
""", unsafe_allow_html=True)

hide_menu_style = """
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)
