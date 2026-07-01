"""
frontend/views/trip_view.py

Responsibility: Render trip creation forms, display active trips in interactive cards,
and manage collaborative group membership.
"""

import streamlit as st
from datetime import date, timedelta
from frontend.styles import render_hero


def render_trip_view(api_client):
    render_hero("🧳 Trip Management Hub", "Organize solo getaways or collaborative group expeditions.")

    tab_my_trips, tab_create = st.tabs(["📋 Active Trips & Groups", "➕ Create New Trip"])

    with tab_create:
        st.markdown("### Launch a New Expedition")
        with st.form("create_trip_form"):
            col1, col2 = st.columns(2)
            with col1:
                dest = st.text_input("Trip Title / Working Destination", placeholder="e.g. October Monsoon Getaway")
                start_dt = st.date_input("Start Date", value=date.today() + timedelta(days=30))
            with col2:
                budget = st.number_input("Budget Per Person (INR)", min_value=1000.0, value=25000.0, step=2500.0)
                end_dt = st.date_input("End Date", value=date.today() + timedelta(days=35))
            
            is_pub = st.checkbox("Public Group Trip (Visible to invitees)", value=True)
            submit_trip = st.form_submit_button("Create Trip", use_container_width=True)

            if submit_trip:
                if not dest:
                    st.error("Please enter a trip title or working destination.")
                else:
                    with st.spinner("Creating trip..."):
                        ok, res = api_client.create_trip(
                            destination=dest,
                            start_date=start_dt.isoformat(),
                            end_date=end_dt.isoformat(),
                            budget_per_person=budget,
                            is_public=is_pub
                        )
                        if ok:
                            st.success("Trip created successfully!")
                            st.rerun()
                        else:
                            st.error(f"Error creating trip: {res}")

    with tab_my_trips:
        with st.spinner("Loading trips..."):
            ok, trips = api_client.list_trips()
            if not ok:
                st.error(f"Failed to load trips: {trips}")
            elif not trips:
                st.info("You haven't created any trips yet. Switch to the 'Create New Trip' tab to begin!")
            else:
                for trip in trips:
                    trip_id = trip.get("id")
                    title = trip.get("destination")
                    start_d = trip.get("start_date")
                    end_d = trip.get("end_date")
                    budget = trip.get("budget_per_person")
                    members = trip.get("members", [])

                    with st.expander(f"🏔️ {title} (ID: {trip_id}) — {start_d} to {end_d}"):
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.markdown(f"**Budget:** ₹{budget:,.2f} per person")
                            st.markdown(f"**Current Members:** {len(members) + 1} travelers")
                            st.caption("Members registered in trip consensus algorithm.")

                        with c2:
                            new_member_id = st.number_input("Add User ID to Group", min_value=1, step=1, key=f"add_m_{trip_id}")
                            if st.button("Add Member", key=f"btn_add_{trip_id}"):
                                m_ok, m_res = api_client.add_trip_member(trip_id, new_member_id)
                                if m_ok:
                                    st.success("Member added!")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {m_res}")
