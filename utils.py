import feedparser
from datetime import datetime, timezone
import email.utils

def get_rss_entries(rss_urls):
    entries = []
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                entries.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", ""),
                })
        except Exception as e:
            print(f"خطا در پردازش {url}: {e}")
    return entries

def is_today(pub_date):
    try:
        pub_dt = datetime(*email.utils.parsedate(pub_date)[:6], tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return pub_dt.date() == now.date()
    except:
        return False
