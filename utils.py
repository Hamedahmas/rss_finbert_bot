# utils.py
import feedparser
import email.utils
from datetime import datetime, timezone

def fetch_rss_entries(url):
    entries = []
    try:
        feed = feedparser.parse(url)
        for item in feed.entries:
            entries.append({
                "title": item.title,
                "link": item.link,
                "published": item.get("published", "")
            })
    except Exception as e:
        print("RSS error:", e)
    return entries

def is_today(pub_date):
    try:
        pub_dt = datetime(*email.utils.parsedate(pub_date)[:6], tzinfo=timezone.utc)
        return pub_dt.date() == datetime.now(timezone.utc).date()
    except:
        return False
