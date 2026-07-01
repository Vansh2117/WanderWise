"""
ml_models/model_trainer.py

Responsibility: Core ML recommendation engine and personality classification.
Implements:
1. PersonalityClassifier: Assigns user vectors to travel personality archetypes.
2. DestinationRecommender: Computes personalized rankings for solo travelers and groups
   using collaborative aggregation strategies (Weighted Average, Least Miserable, Nash Social Welfare).
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional

from ml_models.data_transformation import (
    FEATURE_DIMENSIONS,
    normalize_vector,
    filter_destinations_by_budget,
    get_seasonal_scores_for_month
)

logger = logging.getLogger(__name__)


class PersonalityClassifier:
    """
    Classifies a user's 5D preference vector into one or more of the 8 personality archetypes
    loaded from personality_profiles.csv.
    """
    def __init__(self, df_personalities: pd.DataFrame):
        self.df_personalities = df_personalities.copy()
        self.archetypes = self.df_personalities["personality_type"].str.strip().tolist()
        
        # Build weight matrix (8 x 5)
        weight_cols = [
            "adventure_weight", "culture_weight", "nature_weight",
            "relaxation_weight", "food_social_weight"
        ]
        self.weight_matrix = self.df_personalities[weight_cols].to_numpy(dtype=np.float64)
        
    def classify(self, user_vector: np.ndarray, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Assign personality archetypes using cosine similarity between user vector
        and archetype weight definitions.
        """
        u_vec = normalize_vector(user_vector)
        u_norm = np.linalg.norm(u_vec)
        if u_norm == 0:
            u_norm = 1e-5
            
        similarities = []
        for idx, row_vec in enumerate(self.weight_matrix):
            r_norm = np.linalg.norm(row_vec)
            if r_norm == 0:
                sim = 0.0
            else:
                sim = np.dot(u_vec, row_vec) / (u_norm * r_norm)
            similarities.append(float(sim))
            
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i in top_indices:
            row = self.df_personalities.iloc[i]
            results.append({
                "personality_type": row["personality_type"],
                "description": row.get("description", ""),
                "match_percentage": round(similarities[i] * 100, 1),
                "preferred_climate": row.get("preferred_climate", "any")
            })
        return results


class DestinationRecommender:
    """
    Computes recommendation scores and rankings across India's tourist destinations.
    Supports single-user scoring and multi-user group consensus strategies.
    """
    def __init__(self, df_destinations: pd.DataFrame, df_seasons: pd.DataFrame):
        self.df_destinations = df_destinations.copy()
        self.df_seasons = df_seasons.copy()
        
        # Pre-extract destination feature matrix (N x 5)
        self.dest_matrix = self.df_destinations[FEATURE_DIMENSIONS].to_numpy(dtype=np.float64)
        # Compute norms once for fast cosine similarity
        self.dest_norms = np.linalg.norm(self.dest_matrix, axis=1)
        self.dest_norms[self.dest_norms == 0] = 1e-5  # avoid div by zero
        
    def _compute_cosine_similarity(self, u_vec: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between u_vec and all destination vectors."""
        u_norm = np.linalg.norm(u_vec)
        if u_norm == 0:
            return np.zeros(len(self.df_destinations), dtype=np.float64)
        dots = np.dot(self.dest_matrix, u_vec)
        return dots / (self.dest_norms * u_norm)

    def _generate_explanation(self, row: pd.Series, match_score: float, season_score: float) -> str:
        """Generate a concise human-readable explanation for why a destination was recommended."""
        # Find top dimension of the destination
        scores = {
            "Adventure": row.get("adventure_score", 0),
            "Culture & Heritage": row.get("culture_score", 0),
            "Nature & Scenic": row.get("nature_score", 0),
            "Relaxation": row.get("relaxation_score", 0),
            "Food & Social": row.get("food_social_score", 0)
        }
        top_dim = max(scores, key=scores.get)
        
        parts = [f"{round(match_score, 1)}% preference match highlighted by {top_dim}"]
        if season_score >= 8.0:
            parts.append("peak seasonal weather for travel")
        elif season_score >= 6.0:
            parts.append("pleasant travel conditions")
            
        return "; ".join(parts) + "."

    def recommend_for_user(
        self,
        user_vector: np.ndarray,
        travel_month: Optional[str] = None,
        max_budget_inr: Optional[float] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Rank destinations for a single user.
        """
        u_vec = normalize_vector(user_vector)
        
        # 1. Filter by budget
        df_candidate = filter_destinations_by_budget(self.df_destinations, max_budget_inr)
        indices = df_candidate.index.to_numpy()
        
        # 2. Compute similarity for candidate indices
        all_sims = self._compute_cosine_similarity(u_vec)
        cand_sims = all_sims[indices]
        
        # 3. Get seasonal scores
        seasonal_scores = get_seasonal_scores_for_month(self.df_destinations, self.df_seasons, travel_month)
        cand_seasons = seasonal_scores.iloc[indices].to_numpy()
        
        # 4. Final blended score: 85% preference match + 15% seasonal index
        # Cosine similarity is [0, 1] -> scale to [0, 100]
        pref_scores_100 = cand_sims * 100.0
        season_scores_100 = (cand_seasons / 10.0) * 100.0
        final_scores = 0.85 * pref_scores_100 + 0.15 * season_scores_100
        
        # 5. Sort top_k
        top_order = np.argsort(final_scores)[::-1][:top_k]
        
        results = []
        for pos in top_order:
            orig_idx = indices[pos]
            row = self.df_destinations.loc[orig_idx]
            match_p = float(pref_scores_100[pos])
            s_score = float(cand_seasons[pos])
            
            results.append({
                "destination_id": int(row["id"]),
                "place_name": str(row["place_name"]),
                "city": str(row["city"]),
                "state": str(row["state"]),
                "category": str(row["category"]),
                "rating": float(row.get("rating", 0.0) or 0.0),
                "entrance_fee_inr": float(row.get("entrance_fee_inr", 0.0) or 0.0),
                "match_score": round(float(final_scores[pos]), 1),
                "preference_match_pct": round(match_p, 1),
                "seasonal_score": round(s_score, 1),
                "explanation": self._generate_explanation(row, match_p, s_score)
            })
            
        return results

    def recommend_for_group(
        self,
        member_vectors: List[np.ndarray],
        strategy: str = "weighted_average",
        travel_month: Optional[str] = None,
        max_budget_inr: Optional[float] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Collaborative group destination recommendation.
        
        Strategies:
        - 'weighted_average' / 'average': Maximizes total group happiness by averaging member vectors.
        - 'least_miserable': Focuses on avoiding places where any member has very low satisfaction.
          Uses a blend of minimum satisfaction (60%) and average satisfaction (40%).
        - 'nash_social_welfare': Geometric mean of member satisfactions, balancing fairness across everyone.
        """
        if not member_vectors:
            return []
            
        clean_vecs = [normalize_vector(v) for v in member_vectors]
        num_members = len(clean_vecs)
        
        # 1. Filter candidates by budget
        df_candidate = filter_destinations_by_budget(self.df_destinations, max_budget_inr)
        indices = df_candidate.index.to_numpy()
        
        # 2. Calculate individual match scores [num_members x num_candidates]
        member_sims_list = []
        for u_vec in clean_vecs:
            sims = self._compute_cosine_similarity(u_vec)[indices] * 100.0
            member_sims_list.append(sims)
        member_sim_matrix = np.array(member_sims_list)  # shape (num_members, num_candidates)
        
        # 3. Apply Group Strategy
        strategy_clean = strategy.strip().lower()
        if strategy_clean in ("least_miserable", "least-miserable"):
            # Penalize destinations where minimum member score is low
            min_scores = np.min(member_sim_matrix, axis=0)
            avg_scores = np.mean(member_sim_matrix, axis=0)
            group_pref_scores = 0.60 * min_scores + 0.40 * avg_scores
            strat_label = "Least Miserable (Consensus Safety)"
        elif strategy_clean in ("nash_social_welfare", "nash", "fairness"):
            # Geometric mean across members (ensure min score > 1.0 for log stability)
            clamped = np.maximum(member_sim_matrix, 1.0)
            log_sum = np.sum(np.log(clamped), axis=0)
            group_pref_scores = np.exp(log_sum / num_members)
            strat_label = "Nash Social Welfare (Balanced Fairness)"
        else:
            # Default to Weighted Average
            group_pref_scores = np.mean(member_sim_matrix, axis=0)
            strat_label = "Weighted Average (Max Overall Happiness)"
            
        # 4. Add Seasonal Suitability
        seasonal_scores = get_seasonal_scores_for_month(self.df_destinations, self.df_seasons, travel_month)
        cand_seasons = seasonal_scores.iloc[indices].to_numpy()
        season_scores_100 = (cand_seasons / 10.0) * 100.0
        
        final_scores = 0.85 * group_pref_scores + 0.15 * season_scores_100
        
        # 5. Sort top_k
        top_order = np.argsort(final_scores)[::-1][:top_k]
        
        results = []
        for pos in top_order:
            orig_idx = indices[pos]
            row = self.df_destinations.loc[orig_idx]
            g_pref = float(group_pref_scores[pos])
            s_score = float(cand_seasons[pos])
            
            # Find min and max member satisfaction for transparency
            member_matches = [round(float(member_sim_matrix[m, pos]), 1) for m in range(num_members)]
            
            results.append({
                "destination_id": int(row["id"]),
                "place_name": str(row["place_name"]),
                "city": str(row["city"]),
                "state": str(row["state"]),
                "category": str(row["category"]),
                "rating": float(row.get("rating", 0.0) or 0.0),
                "entrance_fee_inr": float(row.get("entrance_fee_inr", 0.0) or 0.0),
                "match_score": round(float(final_scores[pos]), 1),
                "group_preference_score": round(g_pref, 1),
                "strategy_used": strat_label,
                "member_satisfaction_scores": member_matches,
                "seasonal_score": round(s_score, 1),
                "explanation": f"Group consensus via {strat_label}. Member match range: {min(member_matches)}% - {max(member_matches)}%."
            })
            
        return results
