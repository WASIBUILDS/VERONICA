
import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="VERONICA",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

PAGES = [
    "Dashboard",
    "Game Discovery",
    "OVERDRIVE",
    "Gaming DNA",
    "Deals"
]

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "gaming_dna" not in st.session_state:
    st.session_state.gaming_dna = {}

if "selected_game" not in st.session_state:
    st.session_state.selected_game = None


def go_to(page):
    st.session_state.page = page


def select_game(name):
    st.session_state.selected_game = name


def close_game():
    st.session_state.selected_game = None


# ==========================================
# GAME CATALOGUE
# ==========================================

games = [
    {
        "name": "Elden Ring",
        "genre": "RPG",
        "tags": ["RPG", "Action", "Souls-like", "Adventure"],
        "description": "Explore the Lands Between, face challenging enemies, "
                       "and uncover the mysteries of an enormous fantasy world.",
        "gameplay": ["Exploration", "Challenging Combat", "Open World"],
        "style": "Open World Action RPG",
        "image": "https://cdn.akamai.steamstatic.com/steam/apps/1245620/header.jpg",
        "attributes": {
            "Exploration": 95,
            "Combat": 95,
            "Story": 75,
            "Difficulty": 95,
            "Replayability": 85,
            "Competition": 10
        }
    },
    {
        "name": "Resident Evil 4",
        "genre": "Horror",
        "tags": ["Horror", "Action", "Adventure", "Survival"],
        "description": "A survival horror adventure combining intense combat, "
                       "atmospheric environments, and cinematic storytelling.",
        "gameplay": ["Survival", "Story-driven", "Action"],
        "style": "Survival Horror",
        "image": "https://cdn.akamai.steamstatic.com/steam/apps/2050650/header.jpg",
        "attributes": {
            "Exploration": 55,
            "Combat": 90,
            "Story": 85,
            "Difficulty": 70,
            "Replayability": 75,
            "Competition": 10
        }
    },
    {
        "name": "Hades",
        "genre": "Roguelike",
        "tags": ["Action", "RPG", "Roguelike"],
        "description": "Battle your way out of the underworld through "
                       "fast-paced combat and replayable encounters.",
        "gameplay": ["Fast-paced", "Challenging Combat", "Replayability"],
        "style": "Roguelike Action",
        "image": "https://cdn.akamai.steamstatic.com/steam/apps/1145360/header.jpg",
        "attributes": {
            "Exploration": 40,
            "Combat": 90,
            "Story": 70,
            "Difficulty": 80,
            "Replayability": 100,
            "Competition": 5
        }
    }
]


# ==========================================
# GAMING DNA SCORING
# ==========================================

def calculate_dna(preferences, dislikes):

    scores = {
        "Exploration": 50,
        "Combat": 50,
        "Story": 50,
        "Difficulty": 50,
        "Replayability": 50,
        "Competition": 50
    }

    positive_mapping = {
        "Exploration": ["Exploration", "Open World"],
        "Combat": ["Challenging Combat", "Fast-paced"],
        "Story": ["Story-driven", "Lore"],
        "Difficulty": ["Challenging Combat", "Hard Difficulty"],
        "Replayability": ["Replayability", "Character Progression"],
        "Competition": ["Competitive", "Multiplayer"]
    }

    negative_mapping = {
        "Exploration": ["Linear Levels"],
        "Combat": ["Combat-heavy Gameplay"],
        "Story": ["Story-heavy Gameplay"],
        "Difficulty": ["High Difficulty"],
        "Replayability": ["Repetitive Runs"],
        "Competition": ["Competitive Multiplayer"]
    }

    for attribute, keywords in positive_mapping.items():
        for keyword in keywords:
            if keyword in preferences:
                scores[attribute] += 20

    for attribute, keywords in negative_mapping.items():
        for keyword in keywords:
            if keyword in dislikes:
                scores[attribute] -= 20

    for attribute in scores:
        scores[attribute] = max(0, min(100, scores[attribute]))

    return scores


# ==========================================
# RECOMMENDATION ENGINE
# ==========================================

def calculate_recommendations(dna, catalogue):

    player_scores = dna["scores"]
    favourite_genres = dna["genres"]

    results = []

    for game in catalogue:

        game_scores = game["attributes"]

        # Compare player preferences with game attributes.
        differences = []

        for attribute in player_scores:

            difference = abs(
                player_scores[attribute] - game_scores[attribute]
            )

            differences.append(difference)

        attribute_match = 100 - (
            sum(differences) / len(differences)
        )

        # Compare preferred genres with game genres.
        if favourite_genres:

            genre_matches = sum(
                1 for genre in favourite_genres
                if genre in game["tags"]
            )

            genre_match = (
                genre_matches / len(favourite_genres)
            ) * 100

            # Attributes contribute 75%, genres 25%.
            final_score = (
                attribute_match * 0.75
                + genre_match * 0.25
            )

        else:

            final_score = attribute_match

        # Find the strongest matching gameplay attributes.
        aligned_attributes = []

        for attribute in player_scores:

            if (
                player_scores[attribute] >= 65
                and game_scores[attribute] >= 65
            ):
                aligned_attributes.append(attribute)

        results.append({
            "game": game,
            "score": round(final_score),
            "aligned": aligned_attributes
        })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True
    )


# ==========================================
# DESIGN
# ==========================================

st.markdown("""
<style>

.stApp {
    background:
        linear-gradient(rgba(8,10,20,0.94), rgba(8,10,20,0.96)),
        url("https://images.unsplash.com/photo-1542751371-adc38448a05e");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

[data-testid="stSidebar"] {
    background: rgba(10,12,25,0.97);
    border-right: 1px solid #292943;
}

h1, h2, h3 {
    color: #f1f0ff;
}

p, label, span {
    color: #c4c4d6;
}

.card {
    background: rgba(22,24,42,0.88);
    border: 1px solid #34344e;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 12px;
}

.hero {
    background: linear-gradient(
        110deg,
        rgba(65,35,110,0.75),
        rgba(15,20,42,0.85)
    );
    border: 1px solid #514078;
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 25px;
}

.stButton > button {
    background: #7653d6;
    color: white;
    border: none;
    border-radius: 7px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #9274ed;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("# 🎮 VERONICA")
    st.caption("GAME DISCOVERY & PERFORMANCE")
    st.divider()

    st.radio("NAVIGATION", PAGES, key="page")

    st.divider()
    st.caption("DEVELOPMENT PREVIEW")
    st.caption("Version 0.5")


page = st.session_state.page


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>WELCOME TO VERONICA</h1>
        <p>Your personalized gaming discovery and performance companion.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Explore VERONICA")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 🎯 Game Discovery")
        st.write("Find games that match your gaming preferences.")

        st.button(
            "EXPLORE GAMES",
            on_click=go_to,
            args=("Game Discovery",),
            use_container_width=True
        )

    with col2:

        st.markdown("### ⚡ OVERDRIVE")
        st.write("Explore hardware-aware FPS predictions.")

        st.button(
            "ANALYZE PERFORMANCE",
            on_click=go_to,
            args=("OVERDRIVE",),
            use_container_width=True
        )

    st.divider()
    st.subheader("VERONICA MODULES")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**🎮 Discovery**")
        st.caption("Personalized recommendations.")

    with c2:
        st.markdown("**⚡ OVERDRIVE**")
        st.caption("Hardware-based FPS prediction.")

    with c3:
        st.markdown("**🧬 Gaming DNA**")
        st.caption("Understand your gaming preferences.")


# ==========================================
# GAME DISCOVERY
# ==========================================

elif page == "Game Discovery":

    selected_name = st.session_state.selected_game

    # --------------------------------------
    # GAME DETAILS
    # --------------------------------------

    if selected_name:

        game = next(
            (g for g in games if g["name"] == selected_name),
            None
        )

        if game:

            st.button("← BACK TO DISCOVERY", on_click=close_game)

            st.divider()

            col1, col2 = st.columns([1.1, 1.4])

            with col1:
                st.image(game["image"], use_container_width=True)

            with col2:

                st.title(game["name"])
                st.markdown(f"**{game['style']}**")
                st.write(game["description"])

                st.markdown("**Genres**")
                st.write(" • ".join(game["tags"]))

                st.markdown("**Gameplay Characteristics**")
                st.write(" • ".join(game["gameplay"]))

                if st.button("ADD TO WATCHLIST"):

                    if game["name"] not in st.session_state.watchlist:
                        st.session_state.watchlist.append(game["name"])

                    st.success("Added to your watchlist!")

            st.divider()
            st.subheader("GAME PROFILE")

            st.write("Primary Genre:", game["genre"])
            st.write("Gameplay Style:", game["style"])

            st.info("More game attributes and performance data will be added later.")

    # --------------------------------------
    # DISCOVERY BROWSING
    # --------------------------------------

    else:

        st.title("🎮 GAME DISCOVERY")
        st.caption("Explore games. Discover your next obsession.")

        # PERSONALIZED RECOMMENDATIONS

        dna = st.session_state.gaming_dna

        if dna:

            st.divider()
            st.subheader("🧬 RECOMMENDED FOR YOU")

            st.caption(
                "Ranked using your Gaming DNA and preferred genres."
            )

            recommendations = calculate_recommendations(dna, games)

            for rank, item in enumerate(recommendations, start=1):

                game = item["game"]
                score = item["score"]
                aligned = item["aligned"]

                with st.container(border=True):

                    col1, col2 = st.columns([1, 2])

                    with col1:
                        st.image(
                            game["image"],
                            use_container_width=True
                        )

                    with col2:

                        st.markdown(f"### #{rank}  {game['name']}")

                        st.metric(
                            "DNA MATCH",
                            f"{score}%"
                        )

                        st.progress(score / 100)

                        if aligned:

                            st.caption(
                                "Strong alignment: "
                                + ", ".join(aligned)
                            )

                        else:

                            st.caption(
                                "A broader match based on your preferences."
                            )

                        st.button(
                            "VIEW DETAILS",
                            key=f"recommended_{game['name']}",
                            on_click=select_game,
                            args=(game["name"],)
                        )

        else:

            st.info(
                "Build your Gaming DNA first to unlock personalized recommendations."
            )

            st.button(
                "BUILD GAMING DNA",
                on_click=go_to,
                args=("Gaming DNA",)
            )

        # GENERAL GAME BROWSING

        st.divider()

        st.subheader("EXPLORE ALL GAMES")

        search = st.text_input(
            "Search games",
            placeholder="Search for a game..."
        )

        selected_genre = st.selectbox(
            "Explore by genre",
            [
                "All Genres", "Action", "RPG", "Souls-like",
                "Horror", "Adventure", "Roguelike", "Survival"
            ]
        )

        filtered_games = []

        for game in games:

            matches_search = (
                search.lower() in game["name"].lower()
                if search else True
            )

            matches_genre = (
                selected_genre == "All Genres"
                or selected_genre in game["tags"]
            )

            if matches_search and matches_genre:
                filtered_games.append(game)

        if filtered_games:

            columns = st.columns(3)

            for index, game in enumerate(filtered_games):

                with columns[index % 3]:

                    st.markdown('<div class="card">', unsafe_allow_html=True)

                    st.image(game["image"], use_container_width=True)
                    st.markdown(f"### {game['name']}")
                    st.caption(" • ".join(game["tags"]))
                    st.write(game["description"])

                    st.button(
                        "VIEW DETAILS",
                        key=f"details_{game['name']}",
                        use_container_width=True,
                        on_click=select_game,
                        args=(game["name"],)
                    )

                    st.markdown("</div>", unsafe_allow_html=True)

        else:

            st.info("No games found. Try another search or genre.")

        st.divider()
        st.subheader("⭐ YOUR WATCHLIST")

        if st.session_state.watchlist:

            for name in st.session_state.watchlist:
                st.write(f"🎮 {name}")

        else:

            st.caption("Your watchlist is currently empty.")


# ==========================================
# OVERDRIVE
# ==========================================

elif page == "OVERDRIVE":

    st.title("⚡ OVERDRIVE")
    st.caption("Hardware-aware gaming performance analysis.")

    st.subheader("YOUR HARDWARE")

    col1, col2 = st.columns(2)

    with col1:

        cpu = st.text_input(
            "Processor",
            placeholder="e.g. Intel Core i7-4770"
        )

        gpu = st.text_input(
            "Graphics Card",
            placeholder="e.g. GTX 1050 Ti"
        )

    with col2:

        ram = st.selectbox(
            "RAM",
            ["8 GB", "16 GB", "32 GB", "64 GB"]
        )

        resolution = st.selectbox(
            "Resolution",
            [
                "1280 × 720",
                "1920 × 1080",
                "2560 × 1440",
                "3840 × 2160"
            ]
        )

    st.divider()
    st.subheader("GAME CONFIGURATION")

    game_name = st.text_input(
        "Game",
        placeholder="Enter game name"
    )

    preset = st.selectbox(
        "Graphics Preset",
        ["Low", "Medium", "High", "Ultra"]
    )

    if st.button("PREDICT FPS", use_container_width=True):

        if cpu and gpu and game_name:

            st.info(
                "Hardware configuration received. "
                "The FPS model will be connected here."
            )

        else:

            st.warning("Please enter your CPU, GPU and game name.")

    st.divider()
    st.caption("OVERDRIVE prediction engine: Under development.")


# ==========================================
# GAMING DNA
# ==========================================

elif page == "Gaming DNA":

    st.title("🧬 GAMING DNA")
    st.caption("Your preferences. Your gaming identity.")

    st.markdown("""
    <div class="hero">
        <h3>BUILD YOUR PLAYER PROFILE</h3>
        <p>Tell VERONICA what kind of gaming experiences you enjoy.</p>
    </div>
    """, unsafe_allow_html=True)

    dna = st.session_state.gaming_dna

    st.subheader("1. Genre Preferences")

    favourite_genres = st.multiselect(
        "Which genres do you enjoy?",
        [
            "Action", "RPG", "Horror", "Adventure",
            "FPS", "Strategy", "Survival", "Roguelike"
        ],
        default=dna.get("genres", [])
    )

    favourite_game = st.text_input(
        "Favourite Game",
        value=dna.get("favourite_game", ""),
        placeholder="What game do you love?"
    )

    st.divider()
    st.subheader("2. Gameplay Preferences")

    preferences = st.multiselect(
        "What gameplay experiences do you enjoy?",
        [
            "Exploration",
            "Open World",
            "Challenging Combat",
            "Story-driven",
            "Lore",
            "Fast-paced",
            "Replayability",
            "Character Progression",
            "Competitive",
            "Multiplayer",
            "Hard Difficulty"
        ],
        default=dna.get("preferences", [])
    )

    dislikes = st.multiselect(
        "What experiences do you prefer to avoid?",
        [
            "Linear Levels",
            "Combat-heavy Gameplay",
            "Story-heavy Gameplay",
            "High Difficulty",
            "Repetitive Runs",
            "Competitive Multiplayer"
        ],
        default=dna.get("dislikes", [])
    )

    st.divider()

    if st.button("UPDATE MY GAMING DNA", use_container_width=True):

        scores = calculate_dna(preferences, dislikes)

        st.session_state.gaming_dna = {
            "genres": favourite_genres,
            "favourite_game": favourite_game,
            "preferences": preferences,
            "dislikes": dislikes,
            "scores": scores
        }

        st.success("Gaming DNA updated successfully!")
        st.rerun()

    # PROFILE DISPLAY

    if st.session_state.gaming_dna:

        dna = st.session_state.gaming_dna

        st.divider()
        st.subheader("🧬 YOUR PLAYER PROFILE")

        st.markdown("**Favourite Genres**")
        st.write(", ".join(dna["genres"]) if dna["genres"] else "Not specified")

        st.markdown("**Favourite Game**")
        st.write(dna["favourite_game"] or "Not specified")

        st.divider()
        st.subheader("PLAYER ATTRIBUTE SCORES")

        profile = pd.DataFrame.from_dict(
            dna["scores"],
            orient="index",
            columns=["Score"]
        )

        st.bar_chart(profile)

        st.caption(
            "Scores range from 0 to 100. "
            "50 represents a neutral starting point."
        )

        st.divider()
        st.subheader("PROFILE DATA")
        st.json(dna)


# ==========================================
# DEALS
# ==========================================

elif page == "Deals":

    st.title("🏷️ GAME DEALS")
    st.caption("Find deals for the games you want.")

    desired_game = st.text_input(
        "Search for a game",
        placeholder="e.g. Elden Ring"
    )

    if st.button("ADD TO DEAL WATCHLIST"):

        if desired_game.strip():

            if desired_game not in st.session_state.watchlist:
                st.session_state.watchlist.append(desired_game)

            st.success(f"{desired_game} added to your watchlist!")

        else:

            st.warning("Enter a game name first.")

    st.divider()
    st.subheader("YOUR WATCHLIST")

    if st.session_state.watchlist:

        for name in st.session_state.watchlist:
            st.write(f"🎮 {name}")

    else:

        st.caption("No games added yet.")

    st.divider()

    st.info(
        "Live deal tracking and price comparison "
        "will be connected in a future update."
    )

    st.caption("Currency: USD ($)")


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "VERONICA | Personalized Game Discovery & Performance Prediction System"
)
