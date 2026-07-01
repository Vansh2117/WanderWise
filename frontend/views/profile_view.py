"""
frontend/views/profile_view.py

Responsibility: Interactive Persona Quiz and 1-10 Slider adjustments allowing users
to define their AI travel archetype and save preferences to the database.
"""

import streamlit as st
import json
from frontend.styles import render_hero, render_personality_badge


def render_profile_view(api_client):
    render_hero("🧭 Your AI Travel Profile", "Tune your preferences or complete our interactive quiz to calibrate recommendations.")

    # Load existing preferences if available
    success, prefs = api_client.get_preferences()
    default_climate = "mountains"
    default_style = "adventure"
    default_activities = ["trekking"]
    default_budget = 25000.0
    user_id = 1

    if success and isinstance(prefs, list) and len(prefs) > 0:
        latest = prefs[-1]
        user_id = latest.get("user_id", 1)
        default_climate = latest.get("preferred_climate") or default_climate
        default_style = latest.get("travel_style") or default_style
        default_budget = float(latest.get("max_budget") or default_budget)
        acts = latest.get("preferred_activities")
        if isinstance(acts, str):
            try:
                default_activities = json.loads(acts)
            except Exception:
                default_activities = [acts]
        elif isinstance(acts, list):
            default_activities = acts

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📝 Interactive Persona Quiz")
        with st.form("quiz_form"):
            climate = st.selectbox(
                "Preferred Climate Environment",
                options=["mountains", "coastal", "desert", "tropical", "heritage"],
                index=0 if default_climate == "mountains" else 1
            )
            activities = st.multiselect(
                "Favorite Holiday Activities",
                options=["trekking", "camping", "temples", "museums", "wildlife", "beach", "spa", "shopping", "nightlife", "photography"],
                default=default_activities if all(a in ["trekking", "camping", "temples", "museums", "wildlife", "beach", "spa", "shopping", "nightlife", "photography"] for a in default_activities) else ["trekking"]
            )
            travel_style = st.selectbox(
                "Travel Vibe & Pacing",
                options=["adventure", "luxury", "chill", "cultural", "backpacking"],
                index=0
            )
            max_budget = st.number_input("Max Budget per Trip (INR)", min_value=1000.0, max_value=500000.0, value=default_budget, step=5000.0)
            
            save_quiz = st.form_submit_button("💾 Save Profile & Calibrate Archetype", use_container_width=True)
            if save_quiz:
                # We need user_id; let's get current user info or use stored prefs user_id
                with st.spinner("Saving preferences..."):
                    ok, res = api_client.save_preferences(
                        user_id=user_id,
                        preferred_climate=climate,
                        preferred_activities=activities,
                        travel_style=travel_style,
                        max_budget=max_budget
                    )
                    if ok:
                        st.success("Preferences updated successfully!")
                    else:
                        st.error(f"Error saving preferences: {res}")

    with col2:
        st.markdown("### 🎚️ Fine-Tune 5D Feature Sliders")
        st.markdown("Directly control how our neural collaborative filtering engine weights your destinations:")
        
        adv_score = st.slider("🧗 Adventure & Thrill", min_value=1.0, max_value=10.0, value=8.0, step=0.5)
        cult_score = st.slider("🏛️ History & Culture", min_value=1.0, max_value=10.0, value=6.0, step=0.5)
        nat_score = st.slider("🌲 Scenic Nature & Wildlife", min_value=1.0, max_value=10.0, value=8.5, step=0.5)
        relax_score = st.slider("🏖️ Relaxation & Luxury Spa", min_value=1.0, max_value=10.0, value=4.0, step=0.5)
        food_score = st.slider("🍜 Food, Shopping & Social", min_value=1.0, max_value=10.0, value=7.0, step=0.5)

        st.session_state["slider_scores"] = {
            "adventure_score": adv_score,
            "culture_score": cult_score,
            "nature_score": nat_score,
            "relaxation_score": relax_score,
            "food_social_score": food_score
        }

        st.markdown("#### Preview Your Live Archetype:")
        # We can simulate archetype display or run a quick solo recommendation call
        if adv_score >= 7.5 and nat_score >= 7.5:
            st.markdown(render_personality_badge("Adventurer", 94.0), unsafe_allow_html=True)
            st.markdown(render_personality_badge("Nature Lover", 88.0), unsafe_allow_html=True)
        elif relax_score >= 7.5:
            st.markdown(render_personality_badge("Relaxer", 92.0), unsafe_allow_html=True)
        elif cult_score >= 7.5:
            st.markdown(render_personality_badge("Culturalist", 91.0), unsafe_allow_html=True)
        else:
            st.markdown(render_personality_badge("Balanced Traveler", 85.0), unsafe_allow_html=True)
