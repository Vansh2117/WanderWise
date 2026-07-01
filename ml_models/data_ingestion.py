"""
ml_models/data_ingestion.py

Responsibility: Load the three processed data files into clean DataFrames.
This is the entry point for the entire ML pipeline.
Every other ml_models file imports from here — never from raw CSVs directly.

Files loaded:
    - data/processed/destinations.csv        → 322 places with ML feature scores
    - data/processed/destination_seasons.csv → monthly visit scores per city
    - data/processed/personality_profiles.csv → 8 personality archetypes with weights
"""

import os
import pandas as pd
import logging


logging.basicConfig(
    level=logging.INFO,
    format="[data_ingestion] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

DESTINATIONS_PATH       = os.path.join(DATA_DIR, "destinations.csv")
SEASONS_PATH            = os.path.join(DATA_DIR, "destination_seasons.csv")
PERSONALITY_PATH        = os.path.join(DATA_DIR, "personality_profiles.csv")


# ── Expected columns ───────────────────────────────────────────────────────
# If any of these are missing the file is corrupt or was modified incorrectly.
# We check this on load so errors are caught early rather than deep in the model.

DESTINATIONS_REQUIRED_COLS = [
    "id", "place_name", "city", "state", "zone",
    "place_type", "category", "significance",
    "rating", "review_count_lakhs", "entrance_fee_inr", "visit_duration_hrs",
    "airport_nearby", "dslr_allowed", "best_time_of_day",
    "latitude", "longitude",
    "adventure_score", "culture_score", "nature_score",
    "relaxation_score", "food_social_score"
    
]

SEASONS_REQUIRED_COLS = [
    "city",
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
]

PERSONALITY_REQUIRED_COLS = [
    "personality_type",
    "adventure_weight", "culture_weight", "nature_weight",
    "relaxation_weight", "food_social_weight",
    "budget_sensitivity", "crowd_preference"
]


# ── Core load functions ────────────────────────────────────────────────────

def load_destinations() -> pd.DataFrame:
    """
    Load the master destinations dataset.

    Returns a DataFrame with 322 rows and 25 columns.
    Each row is one tourist place in India with:
      - location info (city, state, zone)
      - classification (category, significance, place_type)
      - quality signals (rating, review count, entrance fee)
      - ML feature scores (adventure, culture, nature, relaxation, food_social)

    Raises:
        FileNotFoundError: if destinations.csv is missing
        ValueError: if required columns are absent
    """
    _check_file_exists(DESTINATIONS_PATH, "destinations.csv")

    df = pd.read_csv(DESTINATIONS_PATH, encoding="utf-8")

    _validate_columns(df, DESTINATIONS_REQUIRED_COLS, "destinations.csv")

    # Ensure ML score columns are numeric — they drive the recommendation model
    score_cols = [
        "adventure_score", "culture_score", "nature_score",
        "relaxation_score", "food_social_score"
    ]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Ensure rating is numeric and within valid range
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Normalize text columns so matching is consistent
    df["city"]  = df["city"].str.strip()
    df["state"] = df["state"].str.strip()
    df["zone"]  = df["zone"].str.strip()

    logger.info(f"Loaded destinations.csv — {len(df)} rows, {len(df.columns)} columns")
    return df


def load_seasons() -> pd.DataFrame:
    """
    Load the seasonal scoring matrix.

    Returns a DataFrame where:
      - Each row is a city
      - Columns jan through dec contain scores 1-10
      - 10 = perfect month to visit, 1 = avoid

    This is used to filter out destinations that are a bad idea
    during the selected trip month before the ML model even runs.

    Raises:
        FileNotFoundError: if destination_seasons.csv is missing
        ValueError: if required columns are absent
    """
    _check_file_exists(SEASONS_PATH, "destination_seasons.csv")

    df = pd.read_csv(SEASONS_PATH, encoding="utf-8")

    _validate_columns(df, SEASONS_REQUIRED_COLS, "destination_seasons.csv")

    # Ensure all month columns are numeric
    month_cols = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
    for col in month_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(5)  # default to 5 if missing

    # Normalize city names for consistent matching
    df["city"] = df["city"].str.strip()

    logger.info(f"Loaded destination_seasons.csv — {len(df)} cities")
    return df


def load_personality_profiles() -> pd.DataFrame:
    """
    Load the personality archetype definitions.

    Returns a DataFrame with 8 rows — one per personality type.
    Each row contains weights for each of the 5 score dimensions.

    These weights are multiplied against a destination's feature scores
    to compute a match score for each personality type.

    Example:
        Adventurer has adventure_weight=10, culture_weight=2
        A trekking destination scores adventure=9, culture=1
        Match = (10*9 + 2*1) / (10+2) = 92/12 = 7.67

    Raises:
        FileNotFoundError: if personality_profiles.csv is missing
        ValueError: if required columns are absent
    """
    _check_file_exists(PERSONALITY_PATH, "personality_profiles.csv")

    df = pd.read_csv(PERSONALITY_PATH, encoding="utf-8")

    _validate_columns(df, PERSONALITY_REQUIRED_COLS, "personality_profiles.csv")

    # Ensure weight columns are numeric
    weight_cols = [
        "adventure_weight", "culture_weight", "nature_weight",
        "relaxation_weight", "food_social_weight"
    ]
    for col in weight_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(1)

    # Normalize personality type names for consistent lookup
    df["personality_type"] = df["personality_type"].str.strip()

    logger.info(f"Loaded personality_profiles.csv — {len(df)} archetypes")
    return df


def load_all() -> dict:
    """
    Convenience function — loads all three datasets at once.

    Returns a dict with keys: 'destinations', 'seasons', 'personalities'

    Usage in other ml_models files:
        from ml_models.data_ingestion import load_all
        data = load_all()
        destinations = data['destinations']
        seasons      = data['seasons']
        personalities = data['personalities']
    """
    logger.info("Loading all datasets...")

    data = {
        "destinations":   load_destinations(),
        "seasons":        load_seasons(),
        "personalities":  load_personality_profiles(),
    }

    logger.info("All datasets loaded successfully.")
    _print_summary(data)

    return data


# ── Helper functions ───────────────────────────────────────────────────────

def _check_file_exists(path: str, filename: str):
    """Raise a clear error if the CSV file is missing."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"\n\n  '{filename}' not found at: {path}\n"
            f"  Make sure you have run the data preparation step and placed\n"
            f"  the processed CSV files in: {DATA_DIR}\n"
        )


def _validate_columns(df: pd.DataFrame, required: list, filename: str):
    """Raise a clear error if any expected columns are missing."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(
            f"\n\n  '{filename}' is missing required columns: {missing}\n"
            f"  Found columns: {list(df.columns)}\n"
            f"  The file may have been modified or is from a different version.\n"
        )


def _print_summary(data: dict):
    """Print a clean summary of what was loaded — useful for debugging."""
    dest = data["destinations"]
    seas = data["seasons"]
    pers = data["personalities"]

    print("\n" + "="*55)
    print("  WanderWise ML Data — Load Summary")
    print("="*55)
    print(f"  Destinations    : {len(dest)} places across {dest['state'].nunique()} states")
    print(f"  Categories      : {dict(dest['category'].value_counts())}")
    print(f"  Seasonal data   : {len(seas)} cities covered")
    print(f"  Personality types: {list(pers['personality_type'])}")
    print(f"  Rating range    : {dest['rating'].min():.1f} – {dest['rating'].max():.1f}")
    print(f"  States covered  : {sorted(dest['state'].unique())}")
    print("="*55 + "\n")