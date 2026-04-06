# WanderWise — AI-Powered Group Travel Planner

WanderWise is an AI-driven travel planning platform that helps individuals and groups collaboratively decide travel destinations and plan trips based on personality, preferences, and group dynamics.

It solves a real-world problem:
"Where should we go?" — when everyone wants something different.

---

## Project Status

This project is currently under active development.

- Frontend interface for user interaction and flow is to be implemented  
- Backend foundation (authentication, database models, APIs) is partially implemented  
- Machine Learning components (personality assignment, recommendation engine, itinerary generation) are in progress  

This repository represents an evolving system with planned ML/AI integration.

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

### Group Travel System (In Progress)

- Create public/private travel groups
- Join groups or travel solo
- (Planned) Group chat functionality

### Personality-Based Recommendation (Planned ML Feature)

- Questionnaire-based personality detection
- Clustering users into travel personas (not final):
  - Explorer
  - Relaxation Seeker
  - Nature Lover
  - Party Lover
  - Culture Enthusiast
  - Urban Wanderer

### Intelligent Destination Recommendation (Planned)

- Uses:
  - Personality vectors
  - User preferences
  - Group aggregation
- Resolves conflicting preferences using ML-based scoring

### Iterative Preference Refinement (Planned)

- Dynamic re-ranking of destinations
- Interactive user input loop

### Smart Itinerary Planning (Planned)

- Budget-aware planning
- Activity suggestions
- Multi-day itinerary generation
- AI-assisted itinerary (future)

---

## ML / AI Components (Planned)

The project is designed to include:

### 1. Personality Clustering

- Algorithm: K-Means
- Input: Questionnaire responses
- Output: Personality classification

### 2. Vector-Based Recommendation System

- Users and destinations represented as vectors
- Matching using cosine similarity

### 3. Group Preference Aggregation

- Methods:
  - Weighted average
  - Minimum satisfaction
  - Nash Social Welfare (geometric mean)

### 4. Ranking System

- Based on:
  - Preference match
  - Budget
  - Travel constraints

### Future ML Enhancements

- Learning-to-Rank (XGBoost / LightGBM)
- Embedding-based recommendations (BERT)
- Budget prediction model
- Feedback-based learning system

---

## Tech Stack

### Frontend

- Streamlit with custom themes

### Backend

- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication
- Pydantic

### Machine Learning (Planned)

- scikit-learn
- NumPy
- Pandas
- (Future) Transformers / Embeddings

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

### 4. Run backend server

uvicorn app:app --reload

### 5. Open API Docs

<http://127.0.0.1:8000/docs>

---

## Example Workflow

1. User signs up
2. Joins or creates a group
3. Inputs preferences
4. (Future) Completes personality questionnaire
5. System suggests destinations
6. Users refine preferences
7. Final destination selected
8. (Future) Itinerary generated

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

- [ ] Personality assignment using K-Means clustering
- [ ] Destination dataset creation
- [ ] Recommendation engine
- [ ] Preference refinement system
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
