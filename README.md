# 🏏 PlayXI — AI Powered Dream11 Team Optimizer

> Built with Python, Streamlit, and Llama 3 AI — picks your best Dream11 XI using head-to-head analysis, team form, and fantasy points prediction.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0-red)
![AI](https://img.shields.io/badge/AI-Llama%203-green)
![IPL](https://img.shields.io/badge/IPL-2026-orange)

---

## 🚀 What is PlayXI?

PlayXI is an AI-powered fantasy cricket team optimizer that helps you pick the best 11 players for Dream11. It combines:

- **Real IPL data** — 278,000+ ball-by-ball records from 2008-2026
- **Head to head analysis** — which team has won more of the last 5 meetings
- **Team form analysis** — is a team scoring big or getting bowled out cheaply?
- **Fantasy points prediction** — calculates each player's last 5 match fantasy points
- **Llama 3 AI** — reasons about all factors and picks the optimal team

---

## 🧠 How It Works
User enters today's Playing 11
↓
AI analyses Head to Head record
↓
AI analyses recent Team Form
↓
Calculates Fantasy Points for last 5 matches
↓
Picks best 11 players + Captain + Vice Captain
↓
Shows detailed analysis and reasoning

---

## 🎯 Features

- ✅ Enter today's actual playing 11 for accurate predictions
- ✅ Head to head win/loss analysis for last 5 meetings
- ✅ Team batting/bowling form — picks more bowlers if a team is getting bowled out
- ✅ Fantasy points calculated using official Dream11 scoring rules
- ✅ Captain = player with highest predicted fantasy points
- ✅ Vice Captain = player with second highest predicted fantasy points
- ✅ Follows all Dream11 rules (min 3 batsmen, min 3 bowlers, max 7 from one team)

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas & NumPy | Data processing and feature engineering |
| Scikit-learn | Machine learning model (Random Forest) |
| Streamlit | Web application UI |
| Groq + Llama 3 | AI reasoning and team selection |
| PuLP | Linear programming for team optimization |
| Pickle | Model serialization |

---

## 📊 Dataset

- **Source:** Cricsheet.org (open cricket data)
- **Size:** 278,205 ball-by-ball records
- **Coverage:** IPL 2008 to 2025
- **Files:** deliveries.csv + matches.csv

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/dhruvWorkss/PlayXI.git
cd PlayXI

# Install dependencies
pip install -r requirements.txt

# Add your API keys to .env file
GROQ_API_KEY=your_groq_api_key_here

# Run the app
streamlit run app/app.py
```

---

## 🔑 API Keys Required

- **Groq API** (free) — [console.groq.com](https://console.groq.com)

---

## 📁 Project Structure
PlayXI/
├── app/
│   └── app.py              ← Streamlit web app
├── data/
│   ├── deliveries_updated_ipl_upto_2025.csv
│   ├── matches_updated_ipl_upto_2025.csv
│   ├── batsman_stats.csv
│   └── bowler_stats.csv
├── notebooks/
│   ├── data_cleaning.ipynb
│   └── 03_ml_model.ipynb
├── src/
│   ├── batsman_model.pkl
│   └── bowler_model.pkl
├── .env                    ← API keys (not committed)
├── .gitignore
└── README.md
---

## 🏏 How to Use

1. Open the app with `streamlit run app/app.py`
2. Select Team 1 and Team 2 from the dropdowns
3. Enter today's playing 11 for both teams (copy from Dream11 or any cricket website)
4. Click **Generate AI Best XI**
5. PlayXI shows you the best team with captain, vice captain and analysis!

---

## 📈 Future Improvements

- [ ] Automatic playing 11 scraping from live sources
- [ ] Live IPL 2026 match data integration
- [ ] Player injury and availability tracking
- [ ] Multiple team suggestions for different strategies
- [ ] Performance tracking — compare predictions vs actual results

---

## 👨‍💻 Built By

**Dhruv** — Final year AI & Data Science student at CMRIT Bangalore

Connect with me on [GitHub](https://github.com/dhruvWorkss)

---

*PlayXI — Where Data Meets Cricket Intelligence* 🏏
