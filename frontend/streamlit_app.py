"""
frontend/streamlit_app.py

Main entry point for WanderWise Streamlit Frontend Portal.
Connects UI styles, API client wrapper, and modular view pages.
"""

import sys
import os

# Ensure root project directory is on sys.path so frontend module imports work cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from frontend.styles import inject_custom_styles
from frontend.api_client import WanderWiseAPIClient
from frontend.views.auth_view import render_auth_view
from frontend.views.profile_view import render_profile_view
from frontend.views.trip_view import render_trip_view
from frontend.views.recommendation_view import render_recommendation_view


st.set_page_config(
    page_title="WanderWise AI Portal",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_styles()

# Initialize API Client
api_client = WanderWiseAPIClient(base_url="http://127.0.0.1:8000")


# Sidebar Navigation & Status
st.sidebar.markdown("## 🌍 WanderWise")
st.sidebar.caption("Smart Trip Recommendation & Collaborative Consensus System")
st.sidebar.markdown("---")

user_email = st.session_state.get("user_email")
if user_email:
    st.sidebar.success(f"👤 Logged in as:\n**{user_email}**")
    if st.sidebar.button("Log Out"):
        st.session_state.pop("token", None)
        st.session_state.pop("user_email", None)
        st.rerun()
else:
    st.sidebar.info("👋 Guest Mode\nPlease log in via Auth screen for private trip access.")

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation Portal",
    options=[
        "🔐 Auth & Account",
        "🧭 AI Persona & Sliders",
        "🧳 Trip Management Hub",
        "✨ AI Recommendations"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 WanderWise AI | Powered by Neural Collaborative Filtering & Game Theory Consensus")

# Route View
if page == "🔐 Auth & Account":
    render_auth_view(api_client)
elif page == "🧭 AI Persona & Sliders":
    render_profile_view(api_client)
elif page == "🧳 Trip Management Hub":
    render_trip_view(api_client)
elif page == "✨ AI Recommendations":
    render_recommendation_view(api_client)
