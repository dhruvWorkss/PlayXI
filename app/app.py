import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(
    page_title="PlayXI - AI Dream11 Optimizer",
    page_icon="🏏",
    layout="wide"
)

st.title("🏏 PlayXI - AI Powered Dream11 Optimizer")
st.markdown("### Head to Head + Team Form + Fantasy Points Analysis")
st.markdown("---")

# IPL 2026 Teams
ipl_teams = [
    "Chennai Super Kings", "Mumbai Indians",
    "Royal Challengers Bengaluru", "Kolkata Knight Riders",
    "Delhi Capitals", "Punjab Kings", "Rajasthan Royals",
    "Sunrisers Hyderabad", "Gujarat Titans", "Lucknow Super Giants"
]

# Team selection
col1, col2 = st.columns(2)
with col1:
    team1 = st.selectbox("Select Team 1 🏏", options=ipl_teams)
with col2:
    team2 = st.selectbox("Select Team 2 🏏", options=ipl_teams, index=1)

st.markdown("---")

# Manual playing 11 input
st.markdown("### 📋 Enter Today's Playing 11")
st.markdown("*Copy from Dream11 app or any cricket website*")

col1, col2 = st.columns(2)
with col1:
    team1_players = st.text_area(
        f"{team1} Playing 11",
        placeholder="Enter one player per line:\nRohit Sharma\nVirat Kohli\n...",
        height=300
    )
with col2:
    team2_players = st.text_area(
        f"{team2} Playing 11",
        placeholder="Enter one player per line:\nRuturaj Gaikwad\nMS Dhoni\n...",
        height=300
    )

st.markdown("---")

def ai_pick_team(team1, team2, team1_players, team2_players):
    prompt = f"""
You are a Dream11 fantasy cricket expert with deep knowledge of IPL 2026.

Match: {team1} vs {team2} in IPL 2026

TODAY'S CONFIRMED PLAYING 11:
{team1}: {team1_players}
{team2}: {team2_players}

IMPORTANT: Only pick players from the lists above. Do not add any other players.

DREAM11 FANTASY POINTS SYSTEM:
Batting:
- 1 point per run
- 1 bonus per boundary, 2 bonus per six
- 8 bonus for 50+, 16 bonus for 100+
- Strike rate bonus (min 10 balls): SR 170+=6pts, 150-170=4pts, 130-150=2pts

Bowling:
- 25 points per wicket
- 4 bonus for 3 wickets, 8 bonus for 4 wickets
- Economy bonus (min 2 overs): Under 5=6pts, 5-6=4pts, 6-7=2pts

Fielding:
- 8 points per catch, 12 per stumping

YOUR TASK:
1. Analyse head to head record between {team1} and {team2} in IPL 2026
2. Analyse recent team form — which team has been scoring more runs, taking more wickets
3. If one team has won more of last 5 meetings — pick MORE players from that team
4. If a team has been getting bowled out cheaply — pick MORE bowlers from the opponent
5. Calculate each player's last 5 IPL 2026 fantasy points
6. Pick 11 players with best average fantasy points
7. Captain = highest predicted fantasy points
8. Vice Captain = second highest predicted fantasy points
9. Rules: min 3 batsmen, min 3 bowlers, max 7 from one team

Respond in this EXACT format:

HEAD TO HEAD ANALYSIS:
- Last 5 meetings: [team1 wins] vs [team2 wins]
- Advantage: [which team and why]

TEAM FORM ANALYSIS:
- {team1} recent scores: [last 3-5 scores]
- {team2} recent scores: [last 3-5 scores]
- Implication: [more batsmen or bowlers from each team]

RECENT FORM (Last 5 IPL 2026 fantasy points):
[Player]: [m1] | [m2] | [m3] | [m4] | [m5] | AVG: [avg]
(list all 22 players)

CAPTAIN: [player] - Predicted: [pts] pts - [reason]
VICE CAPTAIN: [player] - Predicted: [pts] pts - [reason]

DREAM11 TEAM:
1. [player] - [role] - [team] - Avg: [pts] pts
2. [player] - [role] - [team] - Avg: [pts] pts
3. [player] - [role] - [team] - Avg: [pts] pts
4. [player] - [role] - [team] - Avg: [pts] pts
5. [player] - [role] - [team] - Avg: [pts] pts
6. [player] - [role] - [team] - Avg: [pts] pts
7. [player] - [role] - [team] - Avg: [pts] pts
8. [player] - [role] - [team] - Avg: [pts] pts
9. [player] - [role] - [team] - Avg: [pts] pts
10. [player] - [role] - [team] - Avg: [pts] pts
11. [player] - [role] - [team] - Avg: [pts] pts

FINAL ANALYSIS: [4-5 sentences on head to head, team form, captain choice and team balance]
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {e}"

# Generate button
if st.button("🚀 Generate AI Best XI", type="primary"):
    if team1 == team2:
        st.error("Please select two different teams!")
    elif not team1_players or not team2_players:
        st.error("Please enter playing 11 for both teams!")
    else:
        with st.spinner("🤖 AI is analysing head to head, form and fantasy points..."):
            ai_response = ai_pick_team(team1, team2, team1_players, team2_players)

        st.success("✅ AI has picked your Dream11 team!")
        st.markdown("---")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 🤖 AI Team Selection")
            st.markdown(ai_response)

        with col2:
            st.markdown("### 📊 How PlayXI Works")
            st.info("✅ Uses today's actual playing 11")
            st.info("✅ Checks last 5 head to head results")
            st.info("✅ Analyses team batting/bowling form")
            st.info("✅ Calculates last 5 match fantasy points")
            st.info("✅ Captain = highest predicted points")
            st.info("✅ Only picks confirmed playing players")

st.markdown("---")
st.markdown("*PlayXI — Built with ❤️ using Python, Streamlit & Llama 3 AI*")