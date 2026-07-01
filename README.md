# WanderWise — AI-Powered Group Travel Planner

WanderWise is an AI-driven travel planning platform that helps individuals and groups collaboratively decide travel destinations and plan trips based on personality, preferences, and group dynamics.

It solves a real-world problem:
"Where should we go?" — when everyone wants something different.

---

## Project Status

This project is currently under active development.

- Frontend application (Streamlit multi-view portal with custom UI design system) is fully implemented  
- Backend foundation (authentication, database models, APIs, and ML endpoints) is fully implemented  
- Machine Learning components (personality assignment, solo & group recommendation engines, collaborative aggregation strategies) are implemented  

This repository represents a complete, modular, intelligent end-to-end travel recommendation system.

---

## Features

### Frontend (Implemented)

- User-friendly interface for travel planning
- Group creation and exploration flow
- UI for preference selection and interaction
- Designed for collaborative decision-making

### User & Authentication (Backend - Basic)

- Signup/Login (JWT-based)
- User profile structure

### Group Travel System (Implemented)

- Create public/private travel groups
- Invite and manage group members
- Group collaboration for consensus scoring

### Personality-Based Recommendation (Implemented ML Feature)

- Questionnaire & slider-based personality classification
- Classifies travelers into 8 archetypes:
  - Adventurer
  - Relaxation Seeker (Relaxer)
  - Nature Lover
  - Foodie & Socialite
  - Culture Enthusiast (Culturalist)
  - Photographer
  - Budget Traveler

### Intelligent Destination Recommendation (Implemented)

- Uses:
  - 5D feature vectors (Adventure, Culture, Nature, Relaxation, Food/Social)
  - Seasonal weather index matrix across 12 calendar months
  - Group preference aggregation algorithms
- Resolves conflicting group preferences using Game Theory & ML scoring

### Iterative Preference Refinement (Planned)

- Dynamic re-ranking of destinations
- Interactive user input loop

### Smart Itinerary Planning (Planned)

- Budget-aware planning
- Activity suggestions
- Multi-day itinerary generation
- AI-assisted itinerary (future)

---

## ML / AI Components (Implemented)

The project includes:

### 1. Personality Classification
- Algorithm: Normalized vector similarity & archetype matching
- Input: Questionnaire responses & 1-10 slider scores
- Output: Archetype classification with match percentages

### 2. Vector-Based Recommendation System
- Users and 322 Indian destinations represented as 5D vectors
- Matching using cosine similarity blended with monthly seasonal weather suitability

### 3. Group Preference Aggregation
- Implemented Consensus Methods:
  - **Weighted Average**: Maximizes total group happiness
  - **Least Miserable**: Consensus safety to avoid destinations anyone hates
  - **Nash Social Welfare**: Geometric mean for maximum fairness across all trip members

---

## Tech Stack

### Frontend
- Streamlit with custom UI design tokens, glassmorphic cards, and hero gradients

### Backend
- FastAPI
- SQLAlchemy & SQLite
- JWT Authentication (`fastapi-users`, `passlib`, `python-jose`)
- Pydantic v2

### Machine Learning
- scikit-learn
- NumPy
- Pandas

---

## Installation & Setup

### 1. Clone the repository

git clone <https://github.com/Vansh2117/wanderwise.git>
cd wanderwise

### 2. Create environment

conda create -n trip_env python=3.10
conda activate trip_env

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run backend server (Terminal 1)

```powershell
python -m uvicorn app:app --port 8000 --reload
```

### 5. Run Streamlit web application (Terminal 2)

```powershell
python -m streamlit run frontend/streamlit_app.py --server.port 8501
```

### 6. Open Web Application

Open your browser at `http://localhost:8501` (API Docs available at `http://127.0.0.1:8000/docs`).

---

## Example Workflow

1. User signs up and logs in via the Streamlit web app
2. Adjusts 1-10 feature sliders and questionnaire to calibrate their AI Travel Archetype
3. Creates a collaborative group trip and adds friends
4. Toggles between group consensus strategies (*Fairness vs. Excitement vs. Safety*)
5. AI Recommender returns ranked destination cards with match scores and explanations

---

## Problem Solved

Traditional travel planning fails because:

- People have conflicting preferences
- Decision-making becomes inefficient
- No personalization at group level

WanderWise solves this using:

- Personality-based modeling
- Group decision optimization
- Intelligent recommendation systems

---

## Upcoming Features

- [x] Personality assignment using vector similarity & K-Means styling
- [x] Destination dataset creation (322 Indian destinations + seasonal suitability)
- [x] Recommendation engine (Cosine similarity + seasonal index + explanations)
- [x] Preference refinement & group aggregation system (Weighted Average, Least Miserable, Nash Social Welfare)
- [ ] Itinerary generation
- [ ] Group chat (real-time)
- [ ] API integrations (travel data)

---

## Why This Project Matters

This project demonstrates:

- ML system design thinking
- Real-world problem solving
- Full-stack development
- Recommender systems
- Multi-user optimization

---

## Contact

Vansh Sharma  
LinkedIn: <https://www.linkedin.com/in/vanshsharma2117/>  
GitHub: <https://github.com/Vansh2117>

---

## If you like this project, give it a star
