"""
ml_models/data_validation.py

Responsibility: Validate input requests, preference score ranges, month specifications,
and verify data integrity before running inference in model_trainer.py.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

VALID_MONTHS = {
    "1", "01", "jan", "january",
    "2", "02", "feb", "february",
    "3", "03", "mar", "march",
    "4", "04", "apr", "april",
    "5", "05", "may",
    "6", "06", "jun", "june",
    "7", "07", "jul", "july",
    "8", "08", "aug", "august",
    "9", "09", "sep", "september",
    "10", "oct", "october",
    "11", "nov", "november",
    "12", "dec", "december"
}


def validate_slider_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Ensure slider scores are non-negative numeric values.
    Clamps values outside 0-10 range.
    """
    validated = {}
    for k, v in scores.items():
        try:
            val = float(v)
            validated[k] = max(0.0, min(10.0, val))
        except (ValueError, TypeError):
            logger.warning(f"Invalid numeric score for '{k}': {v}. Defaulting to 5.0")
            validated[k] = 5.0
    return validated


def validate_travel_month(month: Optional[Union[str, int]]) -> Optional[str]:
    """
    Validate that the month string is recognized. Returns lowercased normalized string or None.
    """
    if month is None:
        return None
    m_str = str(month).strip().lower()
    if m_str in VALID_MONTHS:
        return m_str
    logger.warning(f"Unrecognized travel month: '{month}'. Seasonal filtering will use defaults.")
    return None


def validate_group_member_vectors(member_vectors: List[np.ndarray]) -> List[np.ndarray]:
    """
    Ensure group recommendation receives valid 5D numeric vectors for each member.
    """
    if not member_vectors:
        raise ValueError("Group recommendation requires at least one member preference vector.")
        
    valid_vecs = []
    for idx, vec in enumerate(member_vectors):
        arr = np.array(vec, dtype=np.float64)
        if arr.shape != (5,):
            logger.warning(f"Member vector {idx} has invalid shape {arr.shape}. Defaulting to 5.0 vector.")
            arr = np.array([5.0, 5.0, 5.0, 5.0, 5.0], dtype=np.float64)
        valid_vecs.append(arr)
        
    return valid_vecs


def validate_dataset_integrity(destinations: pd.DataFrame, personalities: pd.DataFrame) -> bool:
    """
    Verify that loaded dataframes have clean score columns ready for matrix operations.
    """
    score_cols = ["adventure_score", "culture_score", "nature_score", "relaxation_score", "food_social_score"]
    if destinations[score_cols].isna().any().any():
        logger.error("Destinations dataframe contains NaN values in score columns!")
        return False
    if len(personalities) == 0:
        logger.error("Personality profiles dataframe is empty!")
        return False
    return True
