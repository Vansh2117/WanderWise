import pytest
import numpy as np
from ml_models.data_ingestion import load_all
from ml_models.data_transformation import transform_user_preferences, normalize_vector
from ml_models.model_trainer import PersonalityClassifier, DestinationRecommender


@pytest.fixture(scope="module")
def ml_data():
    return load_all()


def test_vector_transformation():
    # Test slider preference
    sliders = {"adventure_score": 9.0, "nature_score": 8.0, "relaxation_score": 2.0}
    vec = transform_user_preferences(slider_scores=sliders)
    assert isinstance(vec, np.ndarray)
    assert len(vec) == 5
    assert vec[0] == 9.0  # adventure
    assert vec[2] == 8.0  # nature
    
    # Test questionnaire categorical inputs
    vec_quest = transform_user_preferences(
        preferred_climate="mountains",
        preferred_activities=["trekking", "camping"],
        travel_style="adventure"
    )
    assert vec_quest[0] >= 8.0  # adventure boosted high


def test_personality_classifier(ml_data):
    classifier = PersonalityClassifier(ml_data["personalities"])
    # Adventurer vector: high adventure & nature, low relaxation
    adv_vec = np.array([10.0, 2.0, 9.0, 1.0, 3.0])
    results = classifier.classify(adv_vec, top_k=2)
    assert len(results) == 2
    assert results[0]["personality_type"] in ("Adventurer", "Nature Lover")


def test_solo_recommendations(ml_data):
    recommender = DestinationRecommender(ml_data["destinations"], ml_data["seasons"])
    adv_vec = np.array([10.0, 2.0, 9.0, 1.0, 3.0])
    recs = recommender.recommend_for_user(adv_vec, travel_month="oct", top_k=5)
    
    assert len(recs) == 5
    assert "explanation" in recs[0]
    assert recs[0]["match_score"] > 0
    # Make sure top results have adventure or nature appeal
    top_place = recs[0]
    assert top_place["destination_id"] > 0


def test_group_recommendation_strategies(ml_data):
    recommender = DestinationRecommender(ml_data["destinations"], ml_data["seasons"])
    # Two diverse members: Member 1 loves trekking, Member 2 loves luxury beach spa
    m1 = np.array([10.0, 2.0, 8.0, 1.0, 3.0])
    m2 = np.array([1.0, 3.0, 5.0, 10.0, 7.0])
    group_vecs = [m1, m2]
    
    recs_avg = recommender.recommend_for_group(group_vecs, strategy="weighted_average", top_k=3)
    recs_lm = recommender.recommend_for_group(group_vecs, strategy="least_miserable", top_k=3)
    recs_nash = recommender.recommend_for_group(group_vecs, strategy="nash_social_welfare", top_k=3)
    
    assert len(recs_avg) == 3
    assert len(recs_lm) == 3
    assert len(recs_nash) == 3
    assert "Least Miserable" in recs_lm[0]["strategy_used"]
    assert "Nash Social Welfare" in recs_nash[0]["strategy_used"]


def test_solo_recommendation_api(client, test_user):
    resp = client.post(
        "/recommendations/solo",
        json={
            "slider_scores": {"adventure_score": 9.0, "nature_score": 8.0},
            "travel_month": "nov",
            "top_k": 3
        },
        headers=test_user["headers"]
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "assigned_personalities" in data
    assert "recommendations" in data
    assert len(data["recommendations"]) == 3


def test_group_recommendation_api(client, test_user):
    # Create a trip first
    trip_resp = client.post(
        "/trips",
        json={
            "destination": "Mystery Trip",
            "start_date": "2026-10-15",
            "end_date": "2026-10-20",
            "budget_per_person": 5000.0,
            "is_public": True
        },
        headers=test_user["headers"]
    )
    trip_id = trip_resp.json()["id"]
    
    # Request group recommendations
    rec_resp = client.post(
        f"/recommendations/group/{trip_id}",
        json={
            "strategy": "nash_social_welfare",
            "top_k": 4
        },
        headers=test_user["headers"]
    )
    assert rec_resp.status_code == 200
    data = rec_resp.json()
    assert len(data["recommendations"]) == 4
    assert "Nash" in data["recommendations"][0]["explanation"]
