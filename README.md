# Getting Started with News Collector 📰

A modern automated news collection workflow that pulls the latest stories from reliable public sources, filters them by your interests, and saves them as easy-to-read Markdown digests.

## What this project does

- Collects news from trusted RSS feeds
- Filters articles based on your configured topics
- Keeps only the selected timeframe:
  - daily
  - 2-day
  - 3-day
  - weekly
- Saves a polished Markdown report in the repository
- Runs automatically on a schedule
- Can also be triggered manually

## Repository structure

- `config/topics.json` — your topic list, schedule mode, and sources
- `.github/workflows/news-digest.yml` — automated GitHub Actions workflow
- `scripts/generate_news_digest.py` — script that fetches and formats the news
- `news/latest.md` — latest generated digest
- `news/archive/` — archived digests by date
- `LICENSE` — MIT license

## How to use it

### 1) Edit your topics

Open `config/topics.json` and customize it:

```json
{
  "topics": ["ai", "cybersecurity", "climate", "health"],
  "schedule_mode": "daily",
  "sources": [
    "https://feeds.reuters.com/reuters/technologyNews",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.apnews.com/rss/apf-topnews.xml"
  ]
}
