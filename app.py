
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

VERSION = "0.9"

PAGES = [
    "Dashboard",
    "Game Discovery",
    "OVERDRIVE",
    "Gaming DNA",
    "Deals"
]

ATTRIBUTES = [
    "Exploration",
    "Combat",
    "Story",
    "Difficulty",
    "Replayability",
    "Competition"
]

ATTRIBUTE_COLUMNS = [
    "exploration",
    "combat",
    "story",
    "difficulty",
    "replayability",
    "competition"
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
# LOAD GAME CATALOGUE
# ==========================================

@st.cache_data
def load_catalogue():

    path = "data/game_catalogue.csv"
    df = pd.read_csv(path)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    required_columns = [
        "title",
        "steam_app_id",
        "category",
        "subgenre",
        "gameplay_tags",
        "primary_attribute",
        "exploration",
        "combat",
        "story",
        "difficulty",
        "replayability",
        "competition"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing CSV columns: {', '.join(missing)}"
        )

    if df["title"].isnull().any():
        raise ValueError("Some games have missing titles.")

    if df["title"].duplicated().any():
        raise ValueError("Duplicate game titles detected.")

    for column in ATTRIBUTE_COLUMNS:

        df[column] = pd.to_numeric(
            df[column],
            errors="raise"
        )

        if not df[column].between(0, 100).all():
            raise ValueError(
                f"Invalid attribute scores in {column}"
            )

    if df["steam_app_id"].isnull().any():
        raise ValueError("Missing Steam App IDs detected.")

    return df


try:
    catalogue_df = load_catalogue()

except Exception as error:
    st.error(f"Catalogue loading failed: {error}")
    st.stop()


# ==========================================
# DATA PROCESSING
# ==========================================

def split_values(value):

    if pd.isna(value):
        return []

    return [
        item.strip()
        for item in str(value).split(";")
        if item.strip()
    ]


def build_games(df):

    catalogue = []

    for _, row in df.iterrows():

        subgenres = split_values(row["subgenre"])
        gameplay = split_values(row["gameplay_tags"])

        category_tags = [
            item.strip()
            for item in str(row["category"]).split("/")
            if item.strip()
        ]

        all_tags = list(dict.fromkeys(
            category_tags + subgenres + gameplay
        ))

        attributes = {
            attribute: int(row[column])
            for attribute, column in zip(
                ATTRIBUTES,
                ATTRIBUTE_COLUMNS
            )
        }

        app_id = str(int(row["steam_app_id"]))

        primary_attribute = str(
            row["primary_attribute"]
        ).strip()

        catalogue.append({

            "name": str(row["title"]),

            "genre": subgenres[0] if subgenres else "Unknown",

            "subgenres": subgenres,

            "category": str(row["category"]),

            "primary_attribute": primary_attribute,

            "tags": all_tags,

            "description": (
                f"Explore {row['title']}, "
                f"a {', '.join(subgenres) if subgenres else 'gaming'} experience "
                f"featuring {', '.join(gameplay[:3]) if gameplay else 'varied gameplay'}."
            ),

            "gameplay": gameplay,

            "style": " / ".join(subgenres),

            "image": (
                f"https://cdn.akamai.steamstatic.com/"
                f"steam/apps/{app_id}/header.jpg"
            ),

            "attributes": attributes

        })

    return catalogue


games = build_games(catalogue_df)


# ==========================================
# GAMING DNA SCORING
# ==========================================

def calculate_dna(preferences, dislikes):

    scores = {
        attribute: 50
        for attribute in ATTRIBUTES
    }

    positive_mapping = {

        "Exploration": [
            "Exploration",
            "Open World"
        ],

        "Combat": [
            "Challenging Combat",
            "Fast-paced"
        ],

        "Story": [
            "Story-driven",
            "Lore"
        ],

        "Difficulty": [
            "Challenging Combat",
            "Hard Difficulty"
        ],

        "Replayability": [
            "Replayability",
            "Character Progression"
        ],

        "Competition": [
            "Competitive",
            "Multiplayer"
        ]

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

        scores[attribute] = max(
            0,
            min(100, scores[attribute])
        )

    return scores


# ==========================================
# RECOMMENDATION ENGINE
# ==========================================

def normalize_text(value):
    return " ".join(
        str(value).lower().replace("-", " ").replace("_", " ").split()
    )


def preference_matches_tags(preference, gameplay_tags):

    aliases = {

        "exploration": [
            "exploration",
            "exploration focused"
        ],

        "open world": [
            "open world",
            "open world exploration"
        ],

        "challenging combat": [
            "challenging combat",
            "precision combat",
            "soulslike",
            "souls like",
            "boss fights",
            "combat"
        ],

        "story driven": [
            "story",
            "narrative",
            "story driven"
        ],

        "lore": [
            "lore",
            "worldbuilding",
            "world building"
        ],

        "fast paced": [
            "fast paced",
            "action",
            "high speed combat"
        ],

        "replayability": [
            "replayability",
            "replayable",
            "roguelike"
        ],

        "character progression": [
            "progression",
            "character builds",
            "character progression",
            "rpg"
        ],

        "competitive": [
            "competitive",
            "pvp",
            "esports"
        ],

        "multiplayer": [
            "multiplayer",
            "co op",
            "cooperative",
            "pvp"
        ],

        "hard difficulty": [
            "hard difficulty",
            "difficult",
            "high difficulty",
            "soulslike",
            "souls like"
        ]

    }

    preference_key = normalize_text(preference)
    wanted_terms = aliases.get(preference_key, [preference_key])

    normalized_tags = {
        normalize_text(tag): str(tag)
        for tag in gameplay_tags
    }

    matches = []

    for normalized_tag, original_tag in normalized_tags.items():

        if any(
            term == normalized_tag
            or term in normalized_tag
            or normalized_tag in term
            for term in wanted_terms
        ):

            matches.append(original_tag)

    return list(dict.fromkeys(matches))


def calculate_recommendations(dna, catalogue):

    player_scores = dna["scores"]

    favourite_genres = dna.get("genres", [])

    favourite_subgenres = dna.get("subgenres", [])

    preferences = dna.get("preferences", [])

    results = []

    for game in catalogue:

        game_scores = game["attributes"]

        # 1. Overall player-to-game attribute similarity

        differences = [

            abs(
                player_scores[attribute]
                - game_scores[attribute]
            )

            for attribute in player_scores

        ]

        attribute_match = 100 - (
            sum(differences) / len(differences)
        )

        # 2. Broad genre overlap

        genre_match = 0
        matched_genres = []

        if favourite_genres:

            game_category_terms = {
                normalize_text(tag)
                for tag in game.get("tags", [])
            }

            matched_genres = [

                genre for genre in favourite_genres

                if normalize_text(genre) in game_category_terms

            ]

            genre_match = (
                len(matched_genres) / len(favourite_genres)
            ) * 100

        # 3. Specific subgenre overlap

        game_subgenres = game.get("subgenres", [])

        game_subgenre_terms = {
            normalize_text(item)
            for item in game_subgenres
        }

        matched_subgenres = [

            item for item in favourite_subgenres

            if normalize_text(item) in game_subgenre_terms

        ]

        subgenre_match = (

            len(matched_subgenres) / len(favourite_subgenres) * 100

            if favourite_subgenres else 0

        )

        # 4. Gameplay preference matching

        matched_preferences = {}

        for preference in preferences:

            matches = preference_matches_tags(
                preference,
                game.get("gameplay", [])
            )

            if matches:
                matched_preferences[preference] = matches

        gameplay_match = (

            len(matched_preferences) / len(preferences) * 100

            if preferences else 0

        )

        # 5. Primary attribute influence

        primary_attribute = normalize_text(
            game.get("primary_attribute", "")
        ).title()

        primary_attribute_affinity = (

            player_scores[primary_attribute]

            if primary_attribute in player_scores

            else 50

        )

        # 6. Weighted recommendation score

        components = [

            (attribute_match, 0.60),

            (primary_attribute_affinity, 0.05)

        ]

        if favourite_genres:
            components.append((genre_match, 0.15))

        if favourite_subgenres:
            components.append((subgenre_match, 0.10))

        if preferences:
            components.append((gameplay_match, 0.10))

        total_weight = sum(
            weight for _, weight in components
        )

        final_score = sum(
            score * weight
            for score, weight in components
        ) / total_weight

        # 7. Generate recommendation explanations

        reasons = []

        if matched_subgenres:

            reasons.append(
                "Subgenre match: "
                + ", ".join(matched_subgenres[:3])
            )

        if matched_genres:

            reasons.append(
                "Genre match: "
                + ", ".join(matched_genres[:3])
            )

        if matched_preferences:

            details = [

                f"{pref} ({', '.join(tags[:2])})"

                for pref, tags in list(
                    matched_preferences.items()
                )[:3]

            ]

            reasons.append(
                "Gameplay match: " + "; ".join(details)
            )

        if (
            primary_attribute in player_scores
            and primary_attribute_affinity >= 65
        ):

            reasons.append(
                f"Primary attribute match: "
                f"{game.get('primary_attribute')} "
                f"aligns with your {primary_attribute} preference"
            )

        # Find the closest attribute similarities

        closest_attributes = sorted(

            player_scores,

            key=lambda attr: abs(
                player_scores[attr] - game_scores[attr]
            )

        )

        strong_attributes = [

            attr for attr in closest_attributes

            if (
                player_scores[attr] >= 60
                and game_scores[attr] >= 60
            )

        ][:2]

        if strong_attributes:

            reasons.append(
                "Attribute alignment: "
                + ", ".join(strong_attributes)
            )

        if not reasons:

            reasons.append(
                "Broad attribute similarity to your Gaming DNA"
            )

        results.append({

            "game": game,

            "score": round(
                max(0, min(100, final_score))
            ),

            "aligned": strong_attributes,

            "reasons": reasons,

            "breakdown": {

                "Attributes": round(attribute_match),

                "Primary attribute": round(
                    primary_attribute_affinity
                ),

                "Genre": (
                    round(genre_match)
                    if favourite_genres else None
                ),

                "Subgenre": (
                    round(subgenre_match)
                    if favourite_subgenres else None
                ),

                "Gameplay": (
                    round(gameplay_match)
                    if preferences else None
                )

            }

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
        linear-gradient(
            rgba(8,10,20,0.94),
            rgba(8,10,20,0.96)
        ),
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

    st.radio(
        "NAVIGATION",
        PAGES,
        key="page"
    )

    st.divider()

    st.caption("DEVELOPMENT PREVIEW")

    st.caption(f"Version {VERSION}")

    st.caption(f"{len(games)} games loaded")


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

        st.write(
            "Find games that match your gaming preferences."
        )

        st.button(
            "EXPLORE GAMES",
            on_click=go_to,
            args=("Game Discovery",),
            use_container_width=True
        )

    with col2:

        st.markdown("### ⚡ OVERDRIVE")

        st.write(
            "Explore hardware-aware FPS predictions."
        )

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

    st.divider()

    st.subheader("CATALOGUE OVERVIEW")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "TOTAL GAMES",
        len(games)
    )

    c2.metric(
        "CATEGORIES",
        catalogue_df["category"].nunique()
    )

    unique_subgenres = {

        genre

        for value in catalogue_df["subgenre"]

        for genre in split_values(value)

    }

    c3.metric(
        "UNIQUE SUBGENRES",
        len(unique_subgenres)
    )


# ==========================================
# GAME DISCOVERY
# ==========================================

elif page == "Game Discovery":

    selected_name = st.session_state.selected_game

    # GAME DETAILS

    if selected_name:

        game = next(

            (
                item for item in games
                if item["name"] == selected_name
            ),

            None

        )

        if game:

            st.button(
                "← BACK TO DISCOVERY",
                on_click=close_game
            )

            st.divider()

            col1, col2 = st.columns([1.1, 1.4])

            with col1:

                st.image(
                    game["image"],
                    use_container_width=True
                )

            with col2:

                st.title(game["name"])

                st.markdown(
                    f"**{game['style']}**"
                )

                st.write(game["description"])

                st.markdown("**Category**")
                st.write(game["category"])

                st.markdown("**Primary Gameplay Attribute**")
                st.write(game["primary_attribute"])

                st.markdown("**Subgenres and Tags**")
                st.write(" • ".join(game["tags"]))

                st.markdown("**Gameplay Characteristics**")

                st.write(

                    " • ".join(game["gameplay"])

                    if game["gameplay"]

                    else "Not specified"

                )

                if st.button("ADD TO WATCHLIST"):

                    if game["name"] not in st.session_state.watchlist:

                        st.session_state.watchlist.append(
                            game["name"]
                        )

                    st.success(
                        "Added to your watchlist!"
                    )

            st.divider()

            st.subheader("GAME ATTRIBUTE PROFILE")

            profile = pd.DataFrame.from_dict(
                game["attributes"],
                orient="index",
                columns=["Score"]
            )

            st.bar_chart(profile)

            st.caption(
                "Initial editorial estimates, not measured game statistics."
            )

    # DISCOVERY BROWSING

    else:

        st.title("🎮 GAME DISCOVERY")

        st.caption(
            "Explore games. Discover your next obsession."
        )

        dna = st.session_state.gaming_dna

        if dna:

            st.divider()

            st.subheader("🧬 RECOMMENDED FOR YOU")

            st.caption(
                "Ranked using your Gaming DNA and preferred genres."
            )

            recommendations = calculate_recommendations(
                dna,
                games
            )

            show_all = st.checkbox(
                "Show all 30 ranked recommendations",
                value=False
            )

            visible_recommendations = (

                recommendations

                if show_all

                else recommendations[:5]

            )

            for rank, item in enumerate(
                visible_recommendations,
                start=1
            ):

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

                        st.markdown(
                            f"### #{rank} {game['name']}"
                        )

                        st.metric(
                            "DNA MATCH",
                            f"{score}%"
                        )

                        st.progress(score / 100)

                        with st.expander("WHY THIS GAME?"):

                            for reason in item["reasons"]:

                                st.markdown(
                                    f"- {reason}"
                                )

                            st.caption(

                                "Match breakdown: "

                                + " | ".join(

                                    f"{label}: {value}%"

                                    for label, value
                                    in item["breakdown"].items()

                                    if value is not None

                                )

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

        # BROWSING FILTERS

        st.divider()

        st.subheader("EXPLORE ALL GAMES")

        search = st.text_input(
            "Search games",
            placeholder="Search for a game..."
        )

        categories = [

            "All Categories"

        ] + sorted(
            catalogue_df["category"].unique().tolist()
        )

        selected_category = st.selectbox(
            "Explore by category",
            categories
        )

        all_genres = sorted({

            genre

            for value in catalogue_df["subgenre"]

            for genre in split_values(value)

        })

        genre_options = ["All Genres"] + all_genres

        selected_genre = st.selectbox(
            "Filter by subgenre",
            genre_options
        )

        filtered_games = []

        for game in games:

            matches_search = (

                search.lower() in (

                    game["name"] + " " +
                    " ".join(game["tags"])

                ).lower()

                if search else True

            )

            matches_category = (

                selected_category == "All Categories"

                or selected_category == game["category"]

            )

            matches_genre = (

                selected_genre == "All Genres"

                or selected_genre in game["subgenres"]

            )

            if (
                matches_search
                and matches_category
                and matches_genre
            ):

                filtered_games.append(game)

        st.caption(
            f"Showing {len(filtered_games)} of {len(games)} games"
        )

        if filtered_games:

            columns = st.columns(3)

            for index, game in enumerate(filtered_games):

                with columns[index % 3]:

                    st.markdown(
                        '<div class="card">',
                        unsafe_allow_html=True
                    )

                    st.image(
                        game["image"],
                        use_container_width=True
                    )

                    st.markdown(
                        f"### {game['name']}"
                    )

                    st.caption(
                        " • ".join(game["tags"][:4])
                    )

                    st.write(game["description"])

                    st.button(
                        "VIEW DETAILS",
                        key=f"details_{game['name']}",
                        use_container_width=True,
                        on_click=select_game,
                        args=(game["name"],)
                    )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

        else:

            st.info(
                "No games found. Try another search or filter."
            )

        st.divider()

        st.subheader("⭐ YOUR WATCHLIST")

        if st.session_state.watchlist:

            for name in st.session_state.watchlist:

                st.write(f"🎮 {name}")

        else:

            st.caption(
                "Your watchlist is currently empty."
            )


# ==========================================
# OVERDRIVE
# ==========================================

elif page == "OVERDRIVE":

    st.title("⚡ OVERDRIVE")

    st.caption(
        "Hardware-aware gaming performance analysis."
    )

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

    if st.button(
        "PREDICT FPS",
        use_container_width=True
    ):

        if cpu and gpu and game_name:

            st.info(
                "Hardware configuration received. "
                "The FPS model will be connected here."
            )

        else:

            st.warning(
                "Please enter your CPU, GPU and game name."
            )

    st.divider()

    st.caption(
        "OVERDRIVE prediction engine: Under development."
    )


# ==========================================
# GAMING DNA
# ==========================================

elif page == "Gaming DNA":

    st.title("🧬 GAMING DNA")

    st.caption(
        "Your preferences. Your gaming identity."
    )

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
            "Action",
            "RPG",
            "Horror",
            "Adventure",
            "FPS",
            "Strategy",
            "Survival",
            "Roguelike"
        ],
        default=dna.get("genres", [])
    )

    available_subgenres = sorted({

        subgenre

        for game in games

        for subgenre in game.get("subgenres", [])

    })

    favourite_subgenres = st.multiselect(
        "Any favourite subgenres? (Optional)",
        available_subgenres,
        default=[
            item for item in dna.get("subgenres", [])
            if item in available_subgenres
        ],
        help="These options come directly from your game catalogue."
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

    if st.button(
        "UPDATE MY GAMING DNA",
        use_container_width=True
    ):

        scores = calculate_dna(
            preferences,
            dislikes
        )

        st.session_state.gaming_dna = {

            "genres": favourite_genres,

            "subgenres": favourite_subgenres,

            "favourite_game": favourite_game,

            "preferences": preferences,

            "dislikes": dislikes,

            "scores": scores

        }

        st.success(
            "Gaming DNA updated successfully!"
        )

        st.rerun()

    # PROFILE DISPLAY

    if st.session_state.gaming_dna:

        dna = st.session_state.gaming_dna

        st.divider()

        st.subheader("🧬 YOUR PLAYER PROFILE")

        st.markdown("**Favourite Genres**")

        st.write(
            ", ".join(dna["genres"])
            if dna["genres"]
            else "Not specified"
        )

        st.markdown("**Favourite Subgenres**")

        st.write(
            ", ".join(dna.get("subgenres", []))
            if dna.get("subgenres")
            else "Not specified"
        )

        st.markdown("**Favourite Game**")

        st.write(
            dna["favourite_game"]
            or "Not specified"
        )

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

    st.caption(
        "Find deals for the games you want."
    )

    desired_game = st.text_input(
        "Search for a game",
        placeholder="e.g. Elden Ring"
    )

    if st.button("ADD TO DEAL WATCHLIST"):

        if desired_game.strip():

            if desired_game not in st.session_state.watchlist:

                st.session_state.watchlist.append(
                    desired_game
                )

            st.success(
                f"{desired_game} added to your watchlist!"
            )

        else:

            st.warning(
                "Enter a game name first."
            )

    st.divider()

    st.subheader("YOUR WATCHLIST")

    if st.session_state.watchlist:

        for name in st.session_state.watchlist:

            st.write(f"🎮 {name}")

    else:

        st.caption(
            "No games added yet."
        )

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
