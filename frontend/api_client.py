"""
frontend/api_client.py

Responsibility: Encapsulate all HTTP requests to the WanderWise FastAPI server.
Manages JWT authentication tokens stored in Streamlit session state and provides
clean error handling.
"""

import requests
import streamlit as st
from typing import Tuple, Dict, Any, List, Optional


class WanderWiseAPIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def _get_headers(self) -> Dict[str, str]:
        token = st.session_state.get("token")
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def signup(self, email: str, password: str) -> Tuple[bool, Any]:
        url = f"{self.base_url}/signup"
        try:
            resp = requests.post(url, json={"email": email, "password": password}, timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def login(self, email: str, password: str) -> Tuple[bool, Any]:
        url = f"{self.base_url}/login"
        try:
            resp = requests.post(url, data={"username": email, "password": password}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("access_token")
                st.session_state["token"] = token
                st.session_state["user_email"] = email
                return True, data
            return False, resp.json().get("detail", "Invalid credentials")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def list_trips(self) -> Tuple[bool, Any]:
        url = f"{self.base_url}/trips"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def create_trip(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget_per_person: float,
        is_public: bool = True
    ) -> Tuple[bool, Any]:
        url = f"{self.base_url}/trips"
        payload = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget_per_person": budget_per_person,
            "is_public": is_public
        }
        try:
            resp = requests.post(url, json=payload, headers=self._get_headers(), timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def add_trip_member(self, trip_id: int, user_id: int) -> Tuple[bool, Any]:
        url = f"{self.base_url}/trips/{trip_id}/members"
        try:
            resp = requests.post(url, json={"trip_id": trip_id, "user_id": user_id}, headers=self._get_headers(), timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def list_trip_members(self, trip_id: int) -> Tuple[bool, Any]:
        url = f"{self.base_url}/trips/{trip_id}/members"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def save_preferences(
        self,
        user_id: int,
        preferred_climate: Optional[str] = None,
        preferred_activities: Optional[List[str]] = None,
        travel_style: Optional[str] = None,
        max_budget: Optional[float] = None
    ) -> Tuple[bool, Any]:
        url = f"{self.base_url}/preferences"
        payload = {
            "user_id": user_id,
            "preferred_climate": preferred_climate,
            "preferred_activities": preferred_activities or [],
            "travel_style": travel_style,
            "max_budget": max_budget
        }
        try:
            resp = requests.post(url, json=payload, headers=self._get_headers(), timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def get_preferences(self) -> Tuple[bool, Any]:
        url = f"{self.base_url}/preferences"
        try:
            resp = requests.get(url, headers=self._get_headers(), timeout=5)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def get_solo_recommendations(
        self,
        slider_scores: Optional[Dict[str, float]] = None,
        preferred_climate: Optional[str] = None,
        preferred_activities: Optional[List[str]] = None,
        travel_style: Optional[str] = None,
        travel_month: Optional[str] = None,
        max_budget_inr: Optional[float] = None,
        top_k: int = 10
    ) -> Tuple[bool, Any]:
        url = f"{self.base_url}/recommendations/solo"
        payload = {
            "slider_scores": slider_scores,
            "preferred_climate": preferred_climate,
            "preferred_activities": preferred_activities,
            "travel_style": travel_style,
            "travel_month": travel_month,
            "max_budget_inr": max_budget_inr,
            "top_k": top_k
        }
        try:
            resp = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def get_group_recommendations(
        self,
        trip_id: int,
        strategy: str = "weighted_average",
        travel_month: Optional[str] = None,
        max_budget_inr: Optional[float] = None,
        top_k: int = 10
    ) -> Tuple[bool, Any]:
        url = f"{self.base_url}/recommendations/group/{trip_id}"
        payload = {
            "strategy": strategy,
            "travel_month": travel_month,
            "max_budget_inr": max_budget_inr,
            "top_k": top_k
        }
        try:
            resp = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                return True, resp.json()
            return False, resp.json().get("detail", f"Error {resp.status_code}")
        except Exception as e:
            return False, f"Connection error: {str(e)}"
