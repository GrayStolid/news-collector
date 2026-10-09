#!/usr/bin/env python3

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

import feedparser
from bs4 import BeautifulSoup

MODE_TO_DAYS = {
    "daily": 1,
    "2-day": 2,
    "3-day": 3,
    "weekly": 7,
}

DEFAULT_SOURCES = [
    "https://feeds.reuters.com/reuters/technologyNews",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/scienceNews",
    "https://feeds.apnews.com/rss/apf-topnews.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
]

def load_config() -> Dict[str, Any]:
    config_path = Path(__file__).resolve().parents[1] / "config" / "topics.json"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
            return data
    return {"topics": ["ai", "technology"], "schedule_mode": "daily", "sources": DEFAULT_SOURCES}

def topic_matches(entry_title: str, entry_summary: str, topics: List[str]) -> bool:
    haystacks = [entry_title or "", entry_summary or ""]
    text = " ".join(haystacks).lower()
    for topic in topics:
        if topic.lower() in text:
            return True
    return False

def parse_entry_date(entry) -> Optional[datetime]:
    date_value = getattr(entry, "published_parsed", None)
    if date_value:
        try:
            return datetime(*date_value[:6], tzinfo=timezone.utc)
        except Exception:
            pass

    raw = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if not raw:
        return None

    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return None

def clean_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(" ", strip=True)

def choose_mode(mode: Optional[str]) -> str:
    selected = (mode or os.getenv("NEWS_MODE") or "daily").strip().lower()
    if selected not in MODE_TO_DAYS:
        return "daily"
    return selected

def get_topics(topics_override: Optional[str]) -> List[str]:
    config = load_config()
    topics = config.get("topics", [])
    override = os.getenv("NEWS_TOPICS") or topics_override
    if override:
        topics = [t.strip() for t in override.split(",") if t.strip()]
    return topics or ["ai", "technology"]

def build_markdown(digests: List[Dict[str, Any]], mode: str, topics: List[str], start: datetime, end: datetime) -> str:
    lines = [
        "# News Digest",
        "",
        f"**Mode:** {mode}",
        f"**Topics:** {', '.join(topics)}",
        f"**Window:** {start.strftime('%Y-%m-%d %H:%M UTC')} to {end.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "---",
        "",
    ]

    if not digests:
        lines.append("No relevant news matched the selected time window and topic filters.")
        return "\n".join(lines) + "\n"

    for item in digests:
        title = item["title"]
        source = item["source"]
        summary = item["summary"]
        link = item["link"]
        published = item["published"]
        image = item.get("image") or ""
        media = item.get("media") or ""

        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"- **Published:** {published}")
        lines.append(f"- **Source:** {source}")
        lines.append(f"- **Link:** [{link}]({link})")
        lines.append("")

        if image:
            lines.append(f"![{title}]({image})")
            lines.append("")
        if media:
            lines.append(f"[Watch media]({media})")
            lines.append("")

        if summary:
            lines.append(summary)
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines) + "\n"

def gather_entries(mode: str, topic_list: List[str]) -> List[Dict[str, Any]]:
    config = load_config()
    sources = config.get("sources", DEFAULT_SOURCES)
    if not sources:
        sources = DEFAULT_SOURCES

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=MODE_TO_DAYS.get(mode, 1))
    if mode == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    matched = []

    for feed_url in sources:
        try:
            feed = feedparser.parse(feed_url)
            for entry in getattr(feed, "entries", []):
                title = getattr(entry, "title", "") or "Untitled item"
                summary = clean_html(getattr(entry, "summary", "") or getattr(entry, "description", "") or "")
                if not topic_matches(title, summary, topic_list):
                    continue

                published = parse_entry_date(entry)
                if published is None:
                    continue

                if published < start:
                    continue

                if published > now:
                    continue

                image = ""
                if getattr(entry, "media_thumbnail", None):
                    image = entry.media_thumbnail[0].get("url") if isinstance(entry.media_thumbnail, list) and entry.media_thumbnail else ""
                if not image and getattr(entry, "media_content", None):
                    media_content = entry.media_content
                    if isinstance(media_content, list) and media_content:
                        image = media_content[0].get("url", "")

                media_url = ""
                if getattr(entry, "links", None):
                    for link in entry.links:
                        if link.get("type", "").startswith("video"):
                            media_url = link.get("href", "")
                            break

                matched.append(
                    {
                        "title": title,
                        "source": feed.feed.get("title", "Unknown feed"),
                        "summary": summary[:500] if summary else "No summary available.",
                        "link": (entry.get("link") or ""),
                        "published": published.strftime("%Y-%m-%d %H:%M UTC"),
                        "image": image,
                        "media": media_url,
                    }
                )
        except Exception as e:
            print(f"Warning: Failed to fetch {feed_url}: {e}")
            continue

    matched.sort(key=lambda item: item["title"].lower())
    return matched

def write_outputs(markdown: str, mode: str, topic_list: List[str], start: datetime, end: datetime) -> None:
    root = Path(__file__).resolve().parents[1]
    news_dir = root / "news"
    news_dir.mkdir(exist_ok=True)
    archive_dir = news_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive_path = archive_dir / f"{run_date}-{mode}.md"
    archive_path.write_text(markdown, encoding="utf-8")

    latest_path = news_dir / "latest.md"
    latest_path.write_text(markdown, encoding="utf-8")

    summary_path = news_dir / "summary.txt"
    summary_path.write_text(
        f"mode={mode}\ntopics={','.join(topic_list)}\nstart={start.isoformat()}\nend={end.isoformat()}\n",
        encoding="utf-8",
    )

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a news digest for configured topics.")
    parser.add_argument("--mode", choices=["daily", "2-day", "3-day", "weekly"], default=None)
    parser.add_argument("--topics", default=None, help="Comma-separated list of topics to include.")
    args = parser.parse_args()

    mode = choose_mode(args.mode)
    topics = get_topics(args.topics)

    now = datetime.now(timezone.utc)
    if mode == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now - timedelta(days=MODE_TO_DAYS[mode])

    digests = gather_entries(mode, topics)
    markdown = build_markdown(digests, mode, topics, start, now)
    write_outputs(markdown, mode, topics, start, now)

    print(f"Generated {len(digests)} article(s) for {mode} window.")

if __name__ == "__main__":
    main()
