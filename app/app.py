import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from groq import Groq
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Page config
st.set_page_config(
    page_title="PlayXI - AI Dream11 Optimizer",
    page_icon="🏏",
    layout="wide"
)

# Title
st.title("🏏 PlayXI - AI Powered Dream11 Optimizer")
st.markdown("### Powered by Live IPL 2026 Data + Llama 3 AI")
st.markdown("---")

# Scrape live IPL 2026 stats
@st.cache_data(ttl=3600)
def get_ipl_2026_stats():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        bat_url = "https://stats.espncricinfo.com/ci/engine/records/batting/most_runs_career.html?id=15946;type=tournament"
        bowl_url = "https://stats.espncricinfo.com/ci/engine/records/bowling/most_wickets_career.html?id=15946;type=tournament"

        bat_response = requests.get(bat_url, headers=headers, timeout=10)
        bat_soup = BeautifulSoup(bat_response.content, 'html.parser')

        bowl_response = requests.get(bowl_url, headers=headers, timeout=10)
        bowl_soup = BeautifulSoup(bowl_response.content, 'html.parser')

        batsmen = []
        bowlers = []

        bat_table = bat_soup.find('table')
        if bat_table:
            rows = bat_table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 8:
                    batsmen.append({
                        'player': cols[0].text.strip(),
                        'matches': cols[2].text.strip(),
                        'runs': cols[4].text.strip(),
                        'avg': cols[6].text.strip(),
                        'sr': cols[7].text.strip(),
                        'role': 'batsman'
                    })

        bowl_table = bowl_soup.find('table')
        if bowl_table:
            rows = bowl_table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 8:
                    bowlers.append({
                        'player': cols[0].text.strip(),
                        'matches': cols[2].text.strip(),
                        'wickets': cols[4].text.strip(),
                        'economy': cols[7].text.strip(),
                        'role': 'bowler'
                    })

        return pd.DataFrame(batsmen), pd.DataFrame(bowlers)

    except Exception as e:
        st.warning(f"Could not fetch live data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Groq AI team picker
def ai_pick_team(batsmen_df, bowlers_df, team1, team2):
    bat_info = batsmen_df.head(20).to_string() if not batsmen_df.empty else "No batting data available"
    bowl_info = bowlers_df.head(20).to_string() if not bowlers_df.empty else "No bowling data available"

    prompt = f"""
You are a Dream11 fantasy cricket expert.

Match: {team1} vs {team2} in IPL 2026

Top batsmen stats from IPL 2026:
{bat_info}

Top bowlers stats from IPL 2026:
{bowl_info}

Pick the best Dream11 team of exactly 11 players following these rules:
1. Minimum 3 batsmen
2. Minimum 3 bowlers
3. Maximum 7 players from one team
4. Include 1 captain and 1 vice captain
5. Consider current IPL 2026 performance

Respond in this exact format:
CAPTAIN: [player name]
VICE CAPTAIN: [player name]
TEAM:
1. [player name] - [role] - [reason in 5 words]
2. [player name] - [role] - [reason in 5 words]
3. [player name] - [role] - [reason in 5 words]
4. [player name] - [role] - [reason in 5 words]
5. [player name] - [role] - [reason in 5 words]
6. [player name] - [role] - [reason in 5 words]
7. [player name] - [role] - [reason in 5 words]
8. [player name] - [role] - [reason in 5 words]
9. [player name] - [role] - [reason in 5 words]
10. [player name] - [role] - [reason in 5 words]
11. [player name] - [role] - [reason in 5 words]

ANALYSIS: [2-3 sentences explaining your team selection strategy]
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {e}"

# IPL 2026 Teams
ipl_teams = [
    "Chennai Super Kings",
    "Mumbai Indians",
    "Royal Challengers Bengaluru",
    "Kolkata Knight Riders",
    "Delhi Capitals",
    "Punjab Kings",
    "Rajasthan Royals",
    "Sunrisers Hyderabad",
    "Gujarat Titans",
    "Lucknow Super Giants"
]

# Team selection
col1, col2 = st.columns(2)
with col1:
    team1 = st.selectbox("Select Team 1 🏏", options=ipl_teams)
with col2:
    team2 = st.selectbox("Select Team 2 🏏", options=ipl_teams, index=1)

st.markdown("---")

# Generate button
if st.button("🚀 Generate AI Best XI", type="primary"):
    if team1 == team2:
        st.error("Please select two different teams!")
    else:
        with st.spinner("🤖 Fetching live IPL 2026 data and consulting AI..."):
            batsmen_df, bowlers_df = get_ipl_2026_stats()
            ai_response = ai_pick_team(batsmen_df, bowlers_df, team1, team2)

        st.success("✅ AI has picked your Dream11 team!")
        st.markdown("---")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 🤖 AI Team Selection")
            st.markdown(ai_response)

        with col2:
            st.markdown("### 📊 Live IPL 2026 Stats Used")
            if not batsmen_df.empty:
                st.markdown("**Top Batsmen:**")
                st.dataframe(batsmen_df[['player', 'runs', 'avg', 'sr']].head(10), use_container_width=True)
            if not bowlers_df.empty:
                st.markdown("**Top Bowlers:**")
                st.dataframe(bowlers_df[['player', 'wickets', 'economy']].head(10), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*PlayXI — Built with ❤️ using Python, Streamlit & Llama 3 AI*")