# PlayXI — Data-backed IPL Fantasy XI Assistant

PlayXI processes 278,000+ IPL ball-by-ball records (2008–3 June 2025), calculates recent player fantasy form, and selects a balanced XI from two user-confirmed squads.

## Live demo

[Open PlayXI](https://playxi-ipl.streamlit.app/)

## What it does

- Cleans raw delivery data and removes duplicate records.
- Builds match-level batting and bowling fantasy features.
- Uses each player's previous five appearances as a transparent prediction baseline.
- Shows real head-to-head results and recent team scores from the local dataset.
- Selects exactly 11 players while enforcing a maximum of seven from one team and minimum batting/bowling coverage.
- Assigns captain and vice-captain from the two highest projections.

The application does not claim access to live fixtures or invent missing statistics with an LLM. Update the dataset and choose the confirmed playing XIs before relying on a recommendation.

## Run locally

```bash
git clone https://github.com/dhruvWorkss/PlayXI.git
cd PlayXI
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

## Rebuild derived player features

```bash
python -m src.pipeline
```

This writes `data/player_features.csv`. The Streamlit app builds the same features from source data and caches them for the session.

## Test

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
PlayXI/
├── app/app.py               # Streamlit application
├── data/                    # Raw and derived IPL data
├── notebooks/               # Exploratory cleaning/model experiments
├── src/pipeline.py          # Reusable feature and optimization logic
├── tests/test_pipeline.py   # Optimizer tests
└── requirements.txt
```

## Method and limitations

The current predictor is deliberately simple: a rolling five-appearance fantasy-points average. It is an interpretable baseline, not a guarantee. Roles are inferred from historical participation. Current player prices, injuries, venue, toss, weather, and matches after 3 June 2025 are not included.

## Next engineering milestones

- Add authoritative squad/role/credit metadata.
- Use chronological backtesting and compare models against the rolling baseline.
- Add venue, opponent, and recency-weighted features.
- Add a scheduled ingestion job and PostgreSQL serving layer.
- Add integration tests and deploy the Streamlit application.

## Tech

Python · Pandas · Streamlit

Data source: [Cricsheet](https://cricsheet.org/)
