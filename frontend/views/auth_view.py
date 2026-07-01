"""
frontend/views/auth_view.py

Responsibility: Render sleek Login and Sign Up tabs allowing users to securely authenticate
against the backend API.
"""

import streamlit as st
from frontend.styles import render_hero


def render_auth_view(api_client):
    render_hero("Welcome to WanderWise 🌍", "Your intelligent AI-powered travel assistant & collaborative itinerary planner.")

    tab_login, tab_signup = st.tabs(["🔑 Log In", "✨ Create Account"])

    with tab_login:
        st.markdown("### Access Your Travel Portal")
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="traveler@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please provide both email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        success, result = api_client.login(email, password)
                        if success:
                            st.success("Successfully logged in!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {result}")

    with tab_signup:
        st.markdown("### Start Your AI Travel Journey")
        with st.form("signup_form"):
            new_email = st.text_input("Email Address", key="su_email", placeholder="traveler@example.com")
            new_password = st.text_input("Choose Password (min 6 chars)", type="password", key="su_pwd")
            confirm_pwd = st.text_input("Confirm Password", type="password", key="su_cpwd")
            submitted_su = st.form_submit_button("Sign Up", use_container_width=True)

            if submitted_su:
                if not new_email or len(new_password) < 6:
                    st.error("Email is required and password must be at least 6 characters.")
                elif new_password != confirm_pwd:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Creating your account..."):
                        success, result = api_client.signup(new_email, new_password)
                        if success:
                            st.success("Account created successfully! Please log in above.")
                        else:
                            st.error(f"Sign up failed: {result}")
