# main.py
from transformers import pipeline
from telegram import Bot
from datetime import datetime
from utils import fetch_rss_entries_from_list, is_today

# تنظیمات تلگرام
TELEGRAM_TOKEN = "7685197740:AAHLS3TBygS_PBeEobf9fyYKQy6M5rANl6s"
TELEGRAM_CHAT_ID = "-1002764995883"

# لیست فیدهای RSS از کانال‌های تلگرام (RSSHub)
RSS_FEED_URLS = [
    "https://rsshub.app/telegram/channel/fxfactoryfarsi",
    "https://rsshub.app/telegram/channel/UtoFx",
    "https://rsshub.app/telegram/channel/xnewsforex",
    "https://rsshub.app/telegram/channel/ForexCalendar",
    "https://rsshub.app/telegram/channel/javaglobal",
    "https://rsshub.app/telegram/channel/porter_news",
    "https://rsshub.app/telegram/channel/ForexMacroNews",
    "https://rsshub.app/telegram/channel/fxstreetforex",
    "https://rsshub.app/telegram/channel/Putin_tramp_mobilizaciya_migrant",
    "https://rsshub.app/telegram/channel/INSIDER_USA_NEWS",
    "https://rsshub.app/telegram/channel/Satoshi_Bad_Whale",
    "https://rsshub.app/telegram/channel/IranNews",
    "https://rsshub.app/telegram/channel/iranfnews",
    "https://rsshub.app/telegram/channel/akhbar_montakhab",
    "https://rsshub.app/telegram/channel/japan",
    "https://rsshub.app/telegram/channel/forexlive"
]

# مدل تحلیل احساسات
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def classify_type(title):
    keywords = ["rate", "inflation", "central bank", "policy", "interest"]
    return "پایدار" if any(k in title.lower() for k in keywords) else "موقتی"

def infer_market(sentiments):
    pos = sentiments.count("positive")
    neg = sentiments.count("negative")
    if pos > neg:
        return "ریسک‌پذیر ✅"
    elif neg > pos:
        return "ریسک‌گریز ❌"
    return "متعادل ⚪️"

def analyze(entries, label):
    sentiments = []
    type_counts = {"پایدار": 0, "موقتی": 0}
    titles = []

    for item in entries:
        title = item["title"]
        result = sentiment_pipeline(title)[0]
        label_ = result["label"].lower()
        sentiments.append(label_)
        type_ = classify_type(title)
        type_counts[type_] += 1
        titles.append(title)

    market_mood = infer_market(sentiments)
    total = len(sentiments)

    major = type_counts["پایدار"]
    minor = type_counts["موقتی"]
    total_types = major + minor
    major_pct = round((major / total_types) * 100) if total_types else 0
    minor_pct = 100 - major_pct

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    sample_titles = " ؛ ".join(titles[:3])

    return f"""
📌 {label}
⏰ تایم تحلیل: {now}
📰 نمونه عناوین: {sample_titles}
📄 تعداد خبرهای تحلیل‌شده: {total}
📊 احساس سرمایه‌گذاران: {market_mood}
📈 نوع جفت‌ارزهای تحت تأثیر: جفت ارزهای پایدار {major_pct}% ؛ موقتی {minor_pct}%
📡 تحلیل با FinBERT
"""

def send_telegram(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print("خطا در ارسال:", e)

def main():
    all_entries = fetch_rss_entries_from_list(RSS_FEED_URLS)

    if not all_entries:
        send_telegram("⛔️ هیچ خبری دریافت نشد.")
        return

    send_telegram(analyze(all_entries, "🟢 تحلیل کلی (تمامی اخبار)"))

    today_entries = [e for e in all_entries if is_today(e["published"])]
    if today_entries:
        send_telegram(analyze(today_entries, "🔵 تحلیل خبرهای امروز"))
    else:
        send_telegram("❗️هیچ خبری برای امروز یافت نشد.")

if __name__ == "__main__":
    main()
