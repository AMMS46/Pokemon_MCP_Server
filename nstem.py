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

# --- Custom CSS for Enhanced UI ---
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* Global styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #FFD700, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .main-subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 1.2rem;
        color: white;
        font-weight: 300;
        opacity: 0.9;
    }

    /* Card styling */
    .feature-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(31, 38, 135, 0.5);
    }

    .card-header {
        font-family: 'Poppins', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Pokemon card styling */
    .pokemon-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
        font-family: 'Poppins', sans-serif;
    }

    .pokemon-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: #FFD700;
        margin-bottom: 0.5rem;
    }

    .pokemon-stat {
        background: rgba(255, 255, 255, 0.1);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }

    .type-badge {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        display: inline-block;
        font-weight: 500;
        font-size: 0.8rem;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        color: #333 !important; /* Changed text color to dark for visibility */
        font-family: 'Poppins', sans-serif !important;
        backdrop-filter: blur(10px) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: rgba(0, 0, 0, 0.6) !important; /* Changed placeholder color to dark */
    }

    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        color: #333 !important; /* Changed text color to dark for visibility */
        font-family: 'Poppins', sans-serif !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Loading animation */
    .loading-pokeball {
        width: 50px;
        height: 50px;
        background: conic-gradient(from 0deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff9ff3, #54a0ff);
        border-radius: 50%;
        animation: spin 2s linear infinite;
        margin: 20px auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Battle result styling */
    .battle-winner {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #333;
        padding: 1rem;
        border-radius: 15px;
        font-weight: 600;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.4);
    }

    .team-member {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4ECDC4;
        display: flex; /* Added for layout of image and text */
        align-items: center; /* Added for layout of image and text */
        gap: 1rem; /* Space between image and text */
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        .feature-card {
            padding: 1rem;
        }
    }

    /* Success/Error styling */
    .stSuccess {
        background: rgba(76, 175, 80, 0.1) !important;
        border: 1px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }

    .stError {
        background: rgba(244, 67, 54, 0.1) !important;
        border: 1px solid rgba(244, 67, 54, 0.3) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }

    .stWarning {
        background: rgba(255, 152, 0, 0.1) !important;
        border: 1px solid rgba(255, 152, 0, 0.3) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }

    .stInfo {
        background: rgba(33, 150, 243, 0.1) !important;
        border: 1px solid rgba(33, 150, 243, 0.3) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }
</style>
""", unsafe_allow_html=True)


MCP_SERVER_URL = "https://pokemon-mcp-server.onrender.com/"


def create_loading_animation():
    """Create a custom loading animation"""
    return """
    <div class="loading-pokeball"></div>
    <p style="text-align: center; color: white; font-family: 'Poppins', sans-serif;">
        Catching data... 🔮
    </p>
    """

def display_pokemon_card(pokemon_data: Dict[str, Any], title: str = None):
    """Display Pokémon info """
    if not pokemon_data:
        st.warning("No Pokémon data to display.")
        return

    with st.container():
        st.markdown(f"""
        <div class="pokemon-card">
            <div class="pokemon-name">
                {'🎯 ' + title if title else ''} {pokemon_data.get('name', 'Unknown')}
                <span style="color: #4ECDC4;">(#{pokemon_data.get('id', 'Unknown')})</span>
            </div>
        """, unsafe_allow_html=True)

        # Create columns for image and basic info
        col1, col2 = st.columns([1, 2])

        with col1:
            if pokemon_data.get('sprite'):
                st.image(pokemon_data['sprite'], width=120)

        with col2:
            # Types
            types_html = ''.join([f'<span class="type-badge">{t}</span>' for t in pokemon_data.get('types', [])])
            st.markdown(f"**Types:** {types_html}", unsafe_allow_html=True)

            # Basic stats
            height = pokemon_data.get('height', 'Unknown')
            weight = pokemon_data.get('weight', 'Unknown')
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <span class="pokemon-stat">📏 {height}m</span>
                <span class="pokemon-stat">⚖️ {weight}kg</span>
            </div>
            """, unsafe_allow_html=True)

            # Abilities
            abilities = pokemon_data.get('abilities', [])
            if abilities:
                abilities_html = ''.join([f'<span class="pokemon-stat">✨ {a}</span>' for a in abilities])
                st.markdown(f"**Abilities:** {abilities_html}", unsafe_allow_html=True)

        # Description
        if pokemon_data.get('description'):
            st.markdown(f"""
            <div style="margin: 1rem 0; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 10px; border-left: 3px solid #FFD700;">
                <strong>🔍 AI Analysis:</strong><br>
                {pokemon_data['description']}
            </div>
            """, unsafe_allow_html=True)

        # Base Stats
        stats = pokemon_data.get('stats', {})
        if stats:
            st.markdown("**📊 Base Stats:**")
            for stat, value in stats.items():
                # Create visuals
                percentage = min(int(value) / 200 * 100, 100)  # Assuming max stat is around 200
                st.markdown(f"""
                <div style="margin: 0.3rem 0;">
                    <span style="color: #FFD700; font-weight: 500;">{stat.title()}:</span>
                    <span style="color: white;">{value}</span>
                    <div style="background: rgba(255,255,255,0.1); border-radius: 10px; height: 8px; margin: 0.2rem 0;">
                        <div style="background: linear-gradient(90deg, #4ECDC4, #FF6B6B); border-radius: 10px; height: 100%; width: {percentage}%;"></div>
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
            error_detail = e.response.json().get('detail', 'An unexpected error occurred.') if e.response.text else 'Server error occurred.'
            return None, f"Server Error: {error_detail}"
    except requests.exceptions.ConnectionError:
        return None, "🔌 Could not connect to the MCP server. Please ensure it's running on localhost:8000"
    except requests.exceptions.Timeout:
        return None, "⏱️ Request timed out. The server might be busy, please try again."
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


# Header
st.markdown("""
<div class="main-header">
    <div class="main-title">🐾 Pokémon MCP Server</div>
    <div class="main-subtitle">
        🚀 Powered by AI • ⚡ Real-time Data • 🎮 Interactive Experience
    </div>
</div>
""", unsafe_allow_html=True)

# Creating tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 **Pokémon Search**", "⚔️ **Battle Arena**", "🛡️ **Strategy Center**", "🤝 **Team Builder**"])

with tab1:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">🔍 Pokémon Explorer</div>
        <p style="color: rgba(255,255,255,0.8); font-family: 'Poppins', sans-serif;">
            Discover detailed information about any Pokémon with AI-powered insights!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        search_name = st.text_input(
            "",
            key="single_pokemon_search",
            placeholder="🎯 Enter Pokémon name (e.g., Pikachu, Charizard, Mewtwo)",
            help="Type any Pokémon name to get detailed information"
        )
    with col2:
        search_button = st.button("🔍 **Search**", key="search_button", use_container_width=True)

    if search_button or (search_name and len(search_name) > 2):
        if search_name:
            with st.spinner("🔮 Gathering Pokémon data..."):
                data, error = make_api_request(f"{MCP_SERVER_URL}/pokemon/{search_name}")

                if data:
                    display_pokemon_card(data)

                    # Add some fun facts
                    st.markdown("""
                    <div style="margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 15px;">
                        <h4 style="color: #4ECDC4; font-family: 'Poppins', sans-serif;">💡 Pro Tips:</h4>
                        <p style="color: rgba(255,255,255,0.8); font-family: 'Poppins', sans-serif;">
                        • Try comparing this Pokémon with others in the Battle Arena!<br>
                        • Check out strategic counters in the Strategy Center!<br>
                        • Use this Pokémon in your dream team!
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
        <div class="card-header">⚔️ Battle Arena</div>
        <p style="color: rgba(255,255,255,0.8); font-family: 'Poppins', sans-serif;">
            Compare Pokémon stats and simulate epic battles with AI analysis!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Pokémon Comparison Section
    st.markdown("### 🆚 Pokémon Comparison")
    col1, col2 = st.columns(2)

    with col1:
        pokemon1_name = st.text_input(
            "🥊 **Fighter 1**",
            key="pokemon1_input",
            placeholder="e.g., Charizard"
        )
    with col2:
        pokemon2_name = st.text_input(
            "🥊 **Fighter 2**",
            key="pokemon2_input",
            placeholder="e.g., Blastoise"
        )

    col1, col2 = st.columns([1, 1])
    with col1:
        compare_button = st.button("📊 **Compare Stats**", key="compare_button", use_container_width=True)
    with col2:
        battle_button_disabled = not (pokemon1_name and pokemon2_name)
        if not battle_button_disabled:
            battle_button = st.button("⚡ **BATTLE!**", key="battle_button", use_container_width=True)
        else:
            st.button("⚡ **BATTLE!**", key="battle_button_disabled", disabled=True, use_container_width=True, help="Enter both Pokémon names first")

    if compare_button and pokemon1_name and pokemon2_name:
        with st.spinner("🔥 Analyzing fighters..."):
            data, error = make_api_request(f"{MCP_SERVER_URL}/compare/{pokemon1_name}/{pokemon2_name}")

            if data:
                st.markdown("### 📊 **Comparison Results**")
                col1, col2 = st.columns(2)

                with col1:
                    display_pokemon_card(data["pokemon1"], "Fighter 1")
                with col2:
                    display_pokemon_card(data["pokemon2"], "Fighter 2")

                # Store for battle
                st.session_state['comparison_pokemon1'] = pokemon1_name
                st.session_state['comparison_pokemon2'] = pokemon2_name

                st.success("✅ Comparison complete! Ready for battle!")
            else:
                st.error(f"❌ {error}")

    # Battle Analysis
    if 'battle_button' in locals() and battle_button:
        with st.spinner("⚡ Epic battle in progress..."):
            time.sleep(1)  # Add dramatic pause
            data, error = make_api_request(f"{MCP_SERVER_URL}/battle/{pokemon1_name}/{pokemon2_name}")

            if data:
                battle_result = data.get('battle_result', {})
                winner = battle_result.get('winner', 'Unknown')
                confidence = battle_result.get('confidence', 'Medium')

                st.markdown(f"""
                <div class="battle-winner">
                    🏆 <strong>WINNER: {winner.upper()}</strong>
                    <br><small>Confidence Level: {confidence}</small>
                </div>
                """, unsafe_allow_html=True)

                # Battle Analysis
                reasoning = battle_result.get('reasoning', 'No analysis available')
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
                    <h4 style="color: #FFD700;">🧠 Battle Analysis</h4>
                    <p style="color: white; line-height: 1.6;">{reasoning}</p>
                </div>
                """, unsafe_allow_html=True)

                # Key Factors
                key_factors = battle_result.get('key_factors', [])
                if key_factors:
                    st.markdown("#### 🎯 **Key Victory Factors:**")
                    for i, factor in enumerate(key_factors, 1):
                        if factor.strip():
                            st.markdown(f"""
                            <div style="background: rgba(76, 175, 80, 0.1); padding: 0.8rem; border-radius: 10px; margin: 0.5rem 0; border-left: 3px solid #4ECDC4;">
                                <strong>{i}.</strong> {factor}
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.error(f"❌ {error}")

with tab3:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">🛡️ Strategy Center</div>
        <p style="color: rgba(255,255,255,0.8); font-family: 'Poppins', sans-serif;">
            Get AI-powered counter recommendations to dominate your battles!
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        counter_pokemon = st.text_input(
            "",
            key="counter_input",
            placeholder="🎯 Enter Pokémon to counter (e.g., Garchomp, Dragonite)",
            help="Find the best counters for any Pokémon"
        )
    with col2:
        counter_button = st.button("🔍 **Find Counters**", key="suggest_counters_button", use_container_width=True)

    if counter_button and counter_pokemon:
        with st.spinner("🧠 Analyzing weaknesses and calculating counters..."):
            data, error = make_api_request(f"{MCP_SERVER_URL}/counters/{counter_pokemon}")

            if data:
                target_pokemon = data.get('target_pokemon', {})
                counters = data.get('counters', [])

                if target_pokemon:
                    st.markdown("### 🎯 **Target Analysis**")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"""
                        <div class="pokemon-card">
                            <div class="pokemon-name">{target_pokemon.get('name', 'Unknown')}</div>
                            <div>Types: {', '.join([f'<span class="type-badge">{t}</span>' for t in target_pokemon.get('types', [])])}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown("""
                        <div style="background: rgba(255,152,0,0.1); padding: 1rem; border-radius: 10px; border-left: 3px solid #FF9800;">
                            <strong>💡 Strategy Tip:</strong><br>
                            Look for Pokémon with type advantages and moves that exploit the target's weaknesses!
                        </div>
                        """, unsafe_allow_html=True)

                if counters:
                    st.markdown("### ⚡ **Recommended Counters**")
                    for i, counter in enumerate(counters, 1):
                        st.markdown(f"""
                        <div class="team-member">
                            <h4 style="color: #4ECDC4; margin-bottom: 0.5rem;">
                                #{i} {counter.get('name', 'Unknown')}
                                <span class="type-badge">{counter.get('type', 'Unknown')}</span>
                            </h4>
                            <div style="color: rgba(255,255,255,0.9); line-height: 1.5;">
                                <strong>🎯 Why it works:</strong> {counter.get('reason', 'Strategic advantage')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("🤔 No specific counters found. Try a different Pokémon!")
            else:
                st.error(f"❌ {error}")

with tab4:
    st.markdown("""
    <div class="feature-card">
        <div class="card-header">🤝 Team Builder</div>
        <p style="color: rgba(255,255,255,0.8); font-family: 'Poppins', sans-serif;">
            Create your dream team with AI-powered suggestions and strategic balance!
        </p>
    </div>
    """, unsafe_allow_html=True)

    team_description = st.text_area(
        "🎨 **Describe Your Dream Team:**",
        placeholder="Example: 'A balanced competitive team with strong offense, one dragon-type, and good type coverage for tournament play'",
        height=100,
        help="Be specific about your preferences - the AI will create a team based on your description!"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("✨ **Generate Dream Team**", key="generate_team_button", use_container_width=True)

    if generate_button and team_description:
        with st.spinner("🎨 AI is crafting your perfect team..."):
            time.sleep(1)  # Add anticipation
            data, error = make_api_request(
                f"{MCP_SERVER_URL}/team/generate",
                method="POST",
                params={"description": team_description}
            )

            if data:
                team = data.get("team", [])

                if team:
                    st.markdown("### 🌟 **Your AI-Generated Dream Team**")
                    st.markdown(f"""
                    <div style="background: rgba(255,215,0,0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0; border-left: 3px solid #FFD700;">
                        <strong>🎯 Team Concept:</strong> {team_description}
                    </div>
                    """, unsafe_allow_html=True)

                    # Display team in a nice grid
                    cols = st.columns(2)
                    for i, member in enumerate(team):
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class="team-member">
                                <h4 style="color: #FFD700; margin-bottom: 0.5rem;">
                                    #{i+1} {member.get('name', 'Unknown')}
                                </h4>
                                <div style="margin: 0.5rem 0;">
                                    <span class="type-badge">{member.get('type', 'Unknown')}</span>
                                </div>
                                <div style="color: rgba(255,255,255,0.9);">
                                    <strong>🎭 Role:</strong> {member.get('role', 'Team Member')}
                                </div>
                            """, unsafe_allow_html=True)
                            if member.get('sprite'): # Display Pokémon photo
                                st.image(member['sprite'], width=100)
                            st.markdown("</div>", unsafe_allow_html=True)


                    st.markdown("""
                    <div style="background: rgba(76,175,80,0.1); padding: 1rem; border-radius: 10px; margin: 2rem 0; border-left: 3px solid #4ECDC4;">
                        <strong>🎉 Team Generated Successfully!</strong><br>
                        Your team has been crafted with strategic balance and synergy in mind.
                        Consider testing these Pokémon in the Battle Arena!
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("🤔 Couldn't generate a team with that description. Try being more specific!")
            else:
                st.error(f"❌ {error}")
    elif generate_button:
        st.warning("⚠️ Please describe your desired team first!")

# --- Enhanced Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 20px; margin: 2rem 0;">
    <p style="color: rgba(255,255,255,0.7); font-family: 'Poppins', sans-serif; font-size: 0.9rem;">
        Developed with ❤️ for Pokémon enthusiasts. Data from PokéAPI. AI insights by Gemini.
    </p>
</div>
""", unsafe_allow_html=True)
