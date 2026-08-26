# 🇮🇳 Mapping India's Innovation Economy

## Where founders build, where startups grow, and where capital flows

This project is an interactive data visualization dashboard that explores
India's startup ecosystem.

---

## 🎯 Project Objectives

The project answers five major questions:

1. Where is startup innovation concentrated?
2. Where is investment flowing?
3. Which industries attract the most funding?
4. How has India's startup ecosystem evolved?
5. What does the journey of an individual founder/startup look like?

---

## 📊 Main Visualizations

### Ecosystem Overview

- Startup concentration by city
- Funding by city
- Funding by industry
- City × Industry heatmap
- Year-wise startup growth
- Year-wise funding
- Funding-round analysis
- Startup count vs funding

### Advanced Features

- Innovation Hotspot Score
- Interactive startup explorer
- Dynamic filters
- Ecosystem timeline
- Automated analytical metrics

### Founder Journey

- Founder
- Startup idea
- Founding year
- Location
- Industry
- First funding
- Major investors
- Growth story
- Current status

---

## 📁 Project Structure

india-innovation-economy/

├── data/
│   ├── raw/
│   │   └── startups.csv
│   └── processed/
│       ├── startups_clean.csv
│       ├── founder_data.csv
│       └── hotspot_scores.csv
│
├── src/
│   ├── 01_inspect_data.py
│   ├── 02_clean_data.py
│   ├── 03_analysis.py
│   └── 04_hotspot_score.py
│
├── dashboard/
│   └── app.py
│
├── assets/
│   └── india_states.geojson
│
├── requirements.txt
└── README.md

---

## ⚙️ Installation

Install dependencies:

```bash
pip install -r requirements.txt