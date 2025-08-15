# Task_05_Descriptive_Stats
This task is to prompt the LLM to correctly answer natural language questions about the Women's Lacrosse Dataset

Earlier the I tried to test the LLMs capabilities in extracting data out of the .pdf files. However, that encountered alot of challenges, not only with alighment of the tables, but also the fact that some of the tables(game_stats) were snapshots and did not have a recognizable tabular structure like the others in the pdf. Libraries like pdfplumber, camelot and pdf2image were used but aligment always was the issue even after telling the LLM what to do. 


Present Update:
The Python script scrapes the website for game details and stores them in separate .csv files for use later. The data in the csv files will be of use to run analysis and take important decisions about players, game strategy, etc.

# Syracuse Women's Lacrosse Stats Analysis

## Overview

This project automates the extraction, processing, and analysis of Syracuse University Women's Lacrosse statistics for the seasons **2023, 2024, and 2025**. It uses both **PDF parsing** (for historical datasets) and **dynamic web scraping with Selenium** (for live website data) to collect game-by-game, player, and team performance statistics.

The analysis then answers key performance questions, such as:

* **Which Syracuse players have improved the most in scoring efficiency year-over-year?**
* **How strong is Syracuse's defense against different opponents over time?**

---

## Repository Structure

```
submission_2/
│-- analysis/
│   │-- q1.py   # Player scoring improvement analysis
│   │-- q2.py   # Defensive strength analysis
│-- data/
│   │-- all_game_by_game_stats_dynamic.csv
│   │-- all_opponent_game_by_game_stats_dynamic.csv
│   │-- all_player_stats_dynamic.csv
│   │-- all_team_stats_dynamic.csv
│-- table_stats_extractor_script.py  # Scraper for website tables
│-- defense_summary_by_year.csv
│-- defense_summary_by_opponent.csv
```
---

## Data Sources

1. **PDF Stats Reports** – Official seasonal stats PDFs from Syracuse University.
2. **Live Stats Pages** – Extracted using Selenium from:

   * `https://cuse.com/sports/womens-lacrosse/stats/<year>`

---

## Features

* **Multi-year data integration**: Merges stats for 2023, 2024, and 2025.
* **Dynamic scraping**: Navigates through tabbed stats sections on the website.
* **PDF table parsing**: Handles text-based and image-based tables.
* **Performance analytics**:

  * Player year-over-year improvement in scoring.
  * Defensive strength analysis (avg. goals allowed, opponent breakdown).

---

## Installation & Requirements

```bash
pip install pandas selenium pdfplumber camelot-py[cv] tabula-py pdf2image
brew install poppler tesseract
```

You will also need **ChromeDriver** installed and accessible in your PATH.

---

## Usage

### 1. Extract & Save Data

```bash
python table_stats_extractor_script.py
```

This generates the CSV datasets for all game-by-game, player, and team stats.

### 2. Run Analysis Scripts

#### Player Improvement Analysis

```bash
python q1.py
```

Outputs players with the largest year-over-year scoring improvement.

#### Defensive Strength Analysis

```bash
python q2.py
```

Outputs defensive summaries by year and by opponent.

---

## Example Insights

* **Player Scoring Growth**: Identifies top improvers in goals per game.
* **Defense Trends**: Shows Syracuse's average goals allowed dropped from 12.8 in 2023 to 12.0 in 2025.

---

## Future Work

* Add **opponent player stats** extraction.
* Visualize trends using matplotlib or seaborn.
* Automate updates as new seasons are published.

---
