"""
frontend/views/recommendation_view.py

Responsibility: Render smart destination recommendations for solo travelers or collaborative
groups, allowing real-time switching between consensus algorithms (Weighted Average,
Least Miserable, Nash Social Welfare).
"""

import streamlit as st
from frontend.styles import render_hero, render_personality_badge


def render_recommendation_view(api_client):
    render_hero("✨ AI Smart Recommendations", "Discover tailored Indian destinations scored by neural feature similarity & seasonal weather indices.")

    col_mode, col_opts = st.columns([1, 2])
    with col_mode:
        mode = st.radio("Recommendation Mode", options=["🎒 Solo Traveler", "👥 Collaborative Group Trip"])

    with col_opts:
        if mode == "🎒 Solo Traveler":
            st.markdown("Uses your live slider scores and questionnaire profile.")
            travel_month = st.selectbox("Planned Travel Month", options=["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], index=9)
            top_k = st.slider("Number of Suggestions", min_value=3, max_value=20, value=6)
            
            if st.button("🚀 Generate Solo Recommendations", use_container_width=True):
                sliders = st.session_state.get("slider_scores", {})
                with st.spinner("Analyzing 322 Indian destinations against your feature vector..."):
                    ok, data = api_client.get_solo_recommendations(
                        slider_scores=sliders if sliders else None,
                        travel_month=travel_month,
                        top_k=top_k
                    )
                    if ok:
                        st.session_state["rec_results"] = data
                    else:
                        st.error(f"Error fetching recommendations: {data}")

        else:
            # Group Trip Mode
            ok_t, trips = api_client.list_trips()
            if not ok_t or not trips:
                st.warning("No active trips found. Please create a trip in the 'Trip Management Hub' first!")
            else:
                trip_options = {f"{t['destination']} (ID: {t['id']})": t['id'] for t in trips}
                selected_trip_label = st.selectbox("Select Group Trip", options=list(trip_options.keys()))
                trip_id = trip_options[selected_trip_label]

                strategy_map = {
                    "⚖️ Max Happiness (Weighted Average)": "weighted_average",
                    "🛡️ Safety First (Least Miserable - No Dislikes)": "least_miserable",
                    "🤝 Fair for Everyone (Nash Social Welfare)": "nash_social_welfare"
                }
                strat_label = st.selectbox("Collaborative Decision Strategy", options=list(strategy_map.keys()))
                strategy = strategy_map[strat_label]

                top_k = st.slider("Number of Group Suggestions", min_value=3, max_value=20, value=6)

                if st.button("🚀 Calculate Group Consensus", use_container_width=True):
                    with st.spinner(f"Computing {strategy} consensus across all trip members..."):
                        ok, data = api_client.get_group_recommendations(
                            trip_id=trip_id,
                            strategy=strategy,
                            top_k=top_k
                        )
                        if ok:
                            st.session_state["rec_results"] = data
                        else:
                            st.error(f"Error computing group recommendations: {data}")

    # Display Results if available
    results = st.session_state.get("rec_results")
    if results:
        st.markdown("---")
        st.markdown("### 🏆 AI Assigned Archetypes")
        personalities = results.get("assigned_personalities", [])
        badge_html = ""
        for p in personalities:
            badge_html += render_personality_badge(p.get("personality_type", "Traveler"), p.get("match_percentage", 85.0))
        st.markdown(badge_html, unsafe_allow_html=True)

        st.markdown("### 📍 Top Recommended Destinations")
        recs = results.get("recommendations", [])
        for rec in recs:
            name = rec.get("place_name")
            city = rec.get("city")
            state = rec.get("state")
            cat = rec.get("category")
            rating = rec.get("rating", 4.5)
            fee = rec.get("entrance_fee_inr", 0.0)
            score = rec.get("match_score", 0.0)
            expl = rec.get("explanation", "Matches your profile strengths.")

            st.markdown(
                f"""
                <div class="destination-card">
                    <div class="destination-title">✨ {name} <span style="font-size:1rem; color:#facc15;">★ {rating}</span></div>
                    <div class="destination-meta">📍 {city}, {state} &nbsp;|&nbsp; 🏷️ Category: {cat} &nbsp;|&nbsp; 🎟️ Fee: ₹{fee:,.0f} &nbsp;|&nbsp; 🔥 AI Match: {score*100:.1f}%</div>
                    <div class="destination-explanation">{expl}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
