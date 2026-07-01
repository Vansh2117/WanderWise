"""
ml_models/data_transformation.py

Responsibility: Transform user preference inputs (questionnaires, categorical preferences,
or direct 1-10 slider scores) into clean, normalized 5-dimensional feature vectors.
Also handles filtering destinations by budget constraints and scoring seasonal suitability.

Dimensions: [adventure, culture, nature, relaxation, food_social]
"""

import numpy as np
import pandas as pd
import json
import logging
from typing import Dict, List, Union, Optional

logger = logging.getLogger(__name__)

# Standard 5 dimensions order used across all ML models
FEATURE_DIMENSIONS = [
    "adventure_score",
    "culture_score",
    "nature_score",
    "relaxation_score",
    "food_social_score"
]

# Mapping month names or numbers to 3-letter column names in destination_seasons.csv
MONTH_MAPPING = {
    "1": "jan", "01": "jan", "jan": "jan", "january": "jan",
    "2": "feb", "02": "feb", "feb": "feb", "february": "feb",
    "3": "mar", "03": "mar", "mar": "mar", "march": "mar",
    "4": "apr", "04": "apr", "apr": "apr", "april": "apr",
    "5": "may", "05": "may", "may": "may",
    "6": "jun", "06": "jun", "jun": "jun", "june": "jun",
    "7": "jul", "07": "jul", "jul": "jul", "july": "jul",
    "8": "aug", "08": "aug", "aug": "aug", "august": "aug",
    "9": "sep", "09": "sep", "sep": "sep", "september": "sep",
    "10": "oct", "oct": "oct", "october": "oct",
    "11": "nov", "nov": "nov", "november": "nov",
    "12": "dec", "dec": "dec", "december": "dec"
}

# Keyword lookup for converting categorical questionnaire responses / travel styles to 5D scores
KEYWORD_TO_DIMENSION_WEIGHTS = {
    # Adventure keywords
    "adventure": {"adventure_score": 9.0, "nature_score": 6.0},
    "hiking": {"adventure_score": 8.0, "nature_score": 8.0},
    "trekking": {"adventure_score": 9.0, "nature_score": 9.0},
    "camping": {"adventure_score": 7.0, "nature_score": 9.0},
    "sports": {"adventure_score": 8.0},
    "skiing": {"adventure_score": 9.0, "nature_score": 7.0},
    "wildlife": {"nature_score": 10.0, "adventure_score": 5.0},
    
    # Culture keywords
    "culture": {"culture_score": 9.0},
    "history": {"culture_score": 10.0},
    "heritage": {"culture_score": 10.0},
    "museum": {"culture_score": 9.0},
    "temple": {"culture_score": 8.0, "relaxation_score": 4.0},
    "religious": {"culture_score": 8.0, "relaxation_score": 5.0},
    "palace": {"culture_score": 9.0},
    "fort": {"culture_score": 9.0, "adventure_score": 3.0},
    "art": {"culture_score": 9.0},
    
    # Nature & Relaxation keywords
    "nature": {"nature_score": 10.0, "relaxation_score": 6.0},
    "beach": {"relaxation_score": 9.0, "nature_score": 7.0, "food_social_score": 5.0},
    "mountains": {"nature_score": 9.0, "adventure_score": 6.0, "relaxation_score": 5.0},
    "resort": {"relaxation_score": 10.0},
    "spa": {"relaxation_score": 10.0},
    "chill": {"relaxation_score": 9.0},
    "scenic": {"nature_score": 9.0, "relaxation_score": 7.0},
    "lake": {"nature_score": 8.0, "relaxation_score": 8.0},
    "waterfall": {"nature_score": 9.0, "adventure_score": 4.0},
    
    # Food & Social keywords
    "food": {"food_social_score": 10.0, "culture_score": 4.0},
    "foodie": {"food_social_score": 10.0, "culture_score": 5.0},
    "nightlife": {"food_social_score": 10.0},
    "shopping": {"food_social_score": 8.0},
    "party": {"food_social_score": 10.0},
    "market": {"food_social_score": 8.0, "culture_score": 5.0},
    "social": {"food_social_score": 9.0}
}


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    """
    Ensure vector is float64 and scaled appropriately between 0 and 10.
    If vector is all zeros, returns a uniform neutral vector (5.0 across all dimensions).
    """
    vec = np.array(vector, dtype=np.float64)
    if np.all(vec == 0):
        return np.array([5.0, 5.0, 5.0, 5.0, 5.0], dtype=np.float64)
    return np.clip(vec, 0.0, 10.0)


def questionnaire_to_vector(
    preferred_climate: Optional[str] = None,
    preferred_activities: Union[List[str], str, None] = None,
    travel_style: Optional[str] = None
) -> np.ndarray:
    """
    Converts categorical questionnaire / preference inputs into a 5D feature vector:
    [adventure, culture, nature, relaxation, food_social]
    """
    scores = {dim: 3.0 for dim in FEATURE_DIMENSIONS}  # Baseline score of 3.0
    
    # Handle activities if passed as JSON string
    if isinstance(preferred_activities, str):
        try:
            preferred_activities = json.loads(preferred_activities)
        except Exception:
            preferred_activities = [preferred_activities]
            
    tokens = []
    if preferred_climate:
        tokens.extend([t.strip().lower() for t in preferred_climate.replace("/", " ").split()])
    if travel_style:
        tokens.extend([t.strip().lower() for t in travel_style.replace("/", " ").split()])
    if preferred_activities and isinstance(preferred_activities, list):
        for act in preferred_activities:
            tokens.extend([t.strip().lower() for t in str(act).replace("/", " ").split()])
            
    # Apply keyword boosts
    matched = False
    for token in tokens:
        for keyword, boosts in KEYWORD_TO_DIMENSION_WEIGHTS.items():
            if keyword in token or token in keyword:
                matched = True
                for dim, val in boosts.items():
                    scores[dim] = max(scores[dim], val)
                    
    # If nothing matched, provide balanced mid-range vector
    if not matched:
        return np.array([5.0, 5.0, 5.0, 5.0, 5.0], dtype=np.float64)
        
    return np.array([scores[dim] for dim in FEATURE_DIMENSIONS], dtype=np.float64)


def transform_user_preferences(
    slider_scores: Optional[Dict[str, float]] = None,
    preferred_climate: Optional[str] = None,
    preferred_activities: Union[List[str], str, None] = None,
    travel_style: Optional[str] = None
) -> np.ndarray:
    """
    Unified entry point to extract a 5D preference vector for a user.
    Supports both numeric sliders and categorical questionnaire inputs.
    If both are provided, slider scores take priority or act as base weights.
    """
    if slider_scores and any(slider_scores.get(dim.replace("_score", ""), 0) > 0 or slider_scores.get(dim, 0) > 0 for dim in FEATURE_DIMENSIONS):
        vec = []
        for dim in FEATURE_DIMENSIONS:
            # Check both full key ("adventure_score") and short key ("adventure")
            short_key = dim.replace("_score", "")
            val = slider_scores.get(dim, slider_scores.get(short_key, 5.0))
            vec.append(float(val))
        return normalize_vector(np.array(vec))
        
    # Fallback to questionnaire / categorical extraction
    return normalize_vector(questionnaire_to_vector(
        preferred_climate=preferred_climate,
        preferred_activities=preferred_activities,
        travel_style=travel_style
    ))


def filter_destinations_by_budget(
    df_destinations: pd.DataFrame,
    max_budget_inr: Optional[float] = None
) -> pd.DataFrame:
    """
    Filter destinations where entrance fee is within the user/group budget constraint.
    If max_budget_inr is None or <= 0, no filtering is applied.
    """
    if max_budget_inr is None or max_budget_inr <= 0:
        return df_destinations
    
    # Filter destinations whose entrance fee is <= max_budget_inr
    # We also keep destinations where entrance fee is 0 or NaN
    fees = pd.to_numeric(df_destinations["entrance_fee_inr"], errors="coerce").fillna(0)
    filtered = df_destinations[fees <= max_budget_inr]
    
    # If budget is extremely strict and filters out almost everything, fall back gracefully
    if len(filtered) < 5:
        logger.warning(f"Strict budget {max_budget_inr} INR returned < 5 destinations. Returning top budget-friendly places.")
        return df_destinations.iloc[fees.argsort()[:20]]
        
    return filtered


def get_seasonal_scores_for_month(
    df_destinations: pd.DataFrame,
    df_seasons: pd.DataFrame,
    travel_month: Optional[str] = None
) -> pd.Series:
    """
    Returns a pandas Series of seasonal suitability scores (1-10) for each destination
    in df_destinations corresponding to the travel_month.
    If travel_month is invalid or None, returns a Series of default scores (7.0).
    """
    if not travel_month:
        return pd.Series(7.0, index=df_destinations.index)
        
    month_col = MONTH_MAPPING.get(str(travel_month).strip().lower())
    if not month_col or month_col not in df_seasons.columns:
        logger.warning(f"Unknown travel month '{travel_month}', using default seasonal score.")
        return pd.Series(7.0, index=df_destinations.index)
        
    # Create a clean lookup map from city -> score for the specified month
    season_map = dict(zip(df_seasons["city"].str.strip().str.lower(), df_seasons[month_col]))
    
    # Map each destination city to its monthly score (defaulting to 6.0 if city not listed)
    city_series = df_destinations["city"].str.strip().str.lower()
    scores = city_series.map(season_map).fillna(6.0)
    return pd.to_numeric(scores)
