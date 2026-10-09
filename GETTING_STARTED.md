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

### 1) Fork or clone the repository

```bash
git clone https://github.com/GrayStolid/news-collector.git
cd news-collector
```

Or click **Fork** on GitHub to create your own copy.

### 2) Edit your topics

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
```

You can change:
- `topics`: keywords you want included
- `schedule_mode`: `daily`, `2-day`, `3-day`, or `weekly`
- `sources`: RSS feeds to scan

### 3) Choose the schedule

The workflow runs by default daily at 8:00 AM UTC.

Edit `.github/workflows/news-digest.yml` if you want another schedule:

```yaml
on:
  schedule:
    - cron: "0 8 * * *"
```

Common cron patterns:
- `0 8 * * *` → daily at 8 AM UTC
- `0 8 * * 1` → weekly every Monday at 8 AM
- `0 8 * * 0,3,6` → every Sunday, Wednesday, Saturday at 8 AM
- `0 0 * * *` → daily at midnight UTC

[Cron expression generator](https://crontab.guru)

### 4) Enable GitHub Actions

In your repository settings:

1. Go to **Settings** → **Actions** → **General**
2. Select **Allow all actions and reusable workflows**
3. Click **Save**

The workflow will now run automatically on the schedule you set.

### 5) Monitor the workflow

After setup, the workflow will:
- Run at your scheduled time
- Fetch RSS articles from configured sources
- Filter articles by your topics
- Keep only articles from the selected time window
- Generate a Markdown digest
- Save it to `news/latest.md`
- Commit and push changes to the repository

Watch progress in the **Actions** tab of your repository.

### 6) Access your digest

After the workflow completes:
- Open `news/latest.md` in your repository
- View it on GitHub (automatically rendered)
- Download it
- Share it
- Archive it

## Exact time-window logic

This is critical:

- `daily` = only today's news
- `2-day` = only the last 2 days
- `3-day` = only the last 3 days
- `weekly` = only the last 7 days

Anything outside that range is automatically excluded. Your digest always matches the selected window exactly.

## Manual trigger

Trigger the workflow anytime without waiting for the schedule:

1. Go to **Actions** tab
2. Select **News Digest** workflow
3. Click **Run workflow**
4. (Optional) Override `mode` and `topics`
5. Click **Run workflow**

The digest generates in ~30 seconds.

## Local generation

Test or generate digests locally:

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Generate digest
python scripts/generate_news_digest.py --mode daily --topics "ai,cybersecurity"
```

Output:
- `news/latest.md` — latest digest
- `news/archive/<date>-<mode>.md` — archived digests
- `news/summary.txt` — metadata

## Output format

Each digest includes:
- Article title (as heading)
- Publication date & source
- Direct link to original article
- Featured image (if available in RSS feed)
- Media/video links (if available)
- Article summary (truncated to 500 chars)

Markdown is rendered beautifully on GitHub and compatible with all Markdown viewers.

## RSS feed sources

Pre-configured reliable sources:
- **Reuters**: Technology, Business, World, Science
- **AP News**: Top Stories
- **BBC News**: General News

Add your own RSS feeds to `config/topics.json` `sources` array.

Common news sources with RSS:
- https://feeds.bloomberg.com/markets/news.rss
- https://www.cnbc.com/id/100003114/device/rss/rss.html
- https://feeds.theverge.com/theverge/index.xml
- https://news.ycombinator.com/rss

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Workflow didn't run | Check Actions tab for errors. Ensure Actions are enabled in Settings. |
| No articles found | Topics may not match current articles. Try broader keywords like "technology" instead of specific terms. Expand time window to `weekly`. |
| Missing images | Not all RSS feeds include images. This is normal. Links still work. |
| Empty digest | Check your topics are spelled correctly. Verify RSS feeds are working. Try manual trigger with `--topics "technology"`. |
| Git push fails | Ensure the workflow has `contents: write` permission in `.github/workflows/news-digest.yml`. |

## Advanced: Custom RSS feeds

Add any RSS feed to `config/topics.json`:

```json
{
  "sources": [
    "https://your-custom-feed.com/rss.xml",
    "https://another-feed.org/feed.xml"
  ]
}
```

Validate feeds before adding:
- Feed must be valid RSS/Atom format
- Must be publicly accessible
- Must include `<title>` and `<link>` elements

## Privacy & data

- No external services beyond RSS feeds
- All processing on GitHub infrastructure
- Article metadata cached locally in `/news/`
- `config/topics.json` is public (part of the repo)
- No user tracking or analytics

## License

This project is licensed under the **MIT License**. See `LICENSE` for details.

**Copyright © 2026 GrayStolid**

You retain full ownership of the original work. The MIT license permits others to use, modify, and distribute the software while preserving your copyright notice.

## Quick checklist

- [ ] Customize `config/topics.json`
- [ ] Set schedule in `.github/workflows/news-digest.yml`
- [ ] Enable Actions in repository Settings
- [ ] Commit and push changes
- [ ] Wait for first workflow run or trigger manually
- [ ] Check `news/latest.md` for your digest
- [ ] Share or archive as needed

## Support & contributions

Found a bug? Want to improve the script?

1. Open an issue describing the problem
2. Fork the repository
3. Create a feature branch
4. Make your changes
5. Submit a pull request

---

**Happy news collecting!** 📰✨
