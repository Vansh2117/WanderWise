"""
frontend/styles.py

Responsibility: Inject rich, state-of-the-art CSS styling into Streamlit for
stunning visual aesthetics (glassmorphic containers, gradients, card components, badges).
"""

import streamlit as st


def inject_custom_styles():
    st.markdown(
        """
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

        /* Root Typography & App Background */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Hero Banner Gradient */
        .hero-banner {
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
            padding: 2.2rem;
            border-radius: 16px;
            color: white;
            box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);
            margin-bottom: 2rem;
        }
        .hero-banner h1 {
            color: #ffffff !important;
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .hero-banner p {
            color: #e0f2fe;
            font-size: 1.15rem;
            margin: 0;
        }

        /* Glassmorphic Cards */
        .destination-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            padding: 1.5rem;
            margin-bottom: 1.25rem;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .destination-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
            border-color: #06b6d4;
        }
        .destination-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #38bdf8;
            margin-bottom: 0.25rem;
        }
        .destination-meta {
            font-size: 0.9rem;
            color: #94a3b8;
            margin-bottom: 0.75rem;
        }
        .destination-explanation {
            font-size: 0.95rem;
            line-height: 1.5;
            color: #e2e8f0;
            background: rgba(15, 23, 42, 0.6);
            padding: 0.85rem;
            border-radius: 8px;
            border-left: 4px solid #38bdf8;
            margin-top: 0.75rem;
        }

        /* Personality Badges */
        .badge-pill {
            display: inline-block;
            padding: 0.35rem 0.85rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.85rem;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .badge-adventurer { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
        .badge-nature { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
        .badge-culture { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid #eab308; }
        .badge-relaxer { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
        .badge-foodie { background: rgba(236, 72, 153, 0.2); color: #f472b6; border: 1px solid #ec4899; }
        .badge-default { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #a855f7; }

        /* Metric Highlights */
        .metric-box {
            background: rgba(30, 41, 59, 0.7);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #38bdf8;
        }
        .metric-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            color: #94a3b8;
            letter-spacing: 0.05em;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_hero(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_personality_badge(personality_type: str, match_pct: float = None):
    p_lower = personality_type.lower()
    badge_class = "badge-default"
    if "adventur" in p_lower: badge_class = "badge-adventurer"
    elif "nature" in p_lower: badge_class = "badge-nature"
    elif "cultur" in p_lower: badge_class = "badge-culture"
    elif "relax" in p_lower: badge_class = "badge-relaxer"
    elif "food" in p_lower: badge_class = "badge-foodie"

    pct_text = f" ({match_pct:.0f}% match)" if match_pct else ""
    return f'<span class="badge-pill {badge_class}">✨ {personality_type}{pct_text}</span>'
