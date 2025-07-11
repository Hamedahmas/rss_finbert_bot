import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from transformers import pipeline
from telegram import Bot
from collections import defaultdict

# ───── تنظیمات ربات تلگرام ─────
TELEGRAM_TOKEN = "7685197740:AAHLS3TBygS_PBeEobf9fyYKQy6M5rANl6s"
TELEGRAM_CHAT_ID = "-1002764995883"

# ───── لیست RSS کانال‌ها ─────
RSS_FEEDS = [
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

# ───── مدل FinBERT ─────
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# ───── دریافت تیترهای امروز ─────
def get_today_rss_headlines(url):
    headlines = []
    try:
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        now = datetime.now(timezone.utc)
        today = now.date()

        for item in root.findall(".//item"):
            title = item.find("title").text.strip()
            link = item.find("link").text.strip()
            pub_date_tag = item.find("pubDate")
            if pub_date_tag is None:
                continue

            try:
                pub_date = datetime.strptime(pub_date_tag.text, "%a, %d %b %Y %H:%M:%S %Z")
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            except:
                continue

            if pub_date.date() == today and pub_date <= now:
                headlines.append((title, link))
    except Exception as e:
        print(f"⚠️ خطا در دریافت {url}: {e}")
    return headlines

# ───── تشخیص پایداری خبر ─────
def classify_sentiment_type(title):
    keywords = ["interest rate", "inflation", "central bank", "monetary policy", "GDP", "unemployment", "ECB", "Fed", "BOJ"]
    for k in keywords:
        if k.lower() in title.lower():
            return "پایدار"
    return "موقتی"

# ───── تشخیص جفت‌ارز از تیتر ─────
def extract_currency_pairs(title, sentiment_label):
    pairs_map = {
        "EUR/USD": ["euro", "eur", "ecb"],
        "USD/JPY": ["yen", "jpy", "boj"],
        "GBP/USD": ["pound", "gbp", "boe"],
        "USD/CHF": ["swiss", "franc", "chf"],
        "AUD/USD": ["australian", "aud", "rba"],
        "USD/CAD": ["canadian", "cad", "boc"]
    }

    found = []
    for pair, keywords in pairs_map.items():
        for k in keywords:
            if k.lower() in title.lower():
                found.append((pair, sentiment_label))
                break
    return found

# ───── تحلیل کلی تیترها ─────
def analyze_all(headlines):
    labels = {"positive": 0, "negative": 0, "neutral": 0}
    currency_stats = defaultdict(lambda: {"count": 0, "type": ""})

    for title, _ in headlines:
        try:
            result = sentiment_pipeline(title)[0]
            label = result["label"].lower()
        except:
            label = "neutral"

        labels[label] += 1
        sentiment_type = classify_sentiment_type(title)
        pairs = extract_currency_pairs(title, label)

        for pair, lbl in pairs:
            currency_stats[pair]["count"] += 1
            currency_stats[pair]["type"] = sentiment_type

    return labels, currency_stats

# ───── ساخت پیام نهایی برای تلگرام ─────
def build_message(headlines, labels, currency_stats):
    total = sum(labels.values())
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    if labels["positive"] > labels["negative"]:
        overall = "صعودی ✅"
    elif labels["negative"] > labels["positive"]:
        overall = "نزولی ❌"
    else:
        overall = "خنثی ⚪️"

    message = f"""🗓 تایم اخبار: ⏰ {now}

📰 تعداد خبرهای تحلیل‌شده: {total}

📊 احساس سرمایه‌گذاران نسبت به بازار: {overall}

📈 جفت‌ارزهای تحت‌تأثیر:"""

    for pair, data in currency_stats.items():
        direction = "⏫" if labels["positive"] > labels["negative"] else "⏬"
        percent = round((data["count"] / total) * 100)
        message += f"\n{pair} {direction}{data['type']} {percent}%"

    message += "\n\n📡 تحلیل اتوماتیک با FinBERT"
    return message

# ───── ارسال پیام به تلگرام ─────
def send_telegram_message(text):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print("❌ خطا در ارسال پیام:", e)

# ───── اجرای اصلی ─────
def main():
    all_headlines = []
    for url in RSS_FEEDS:
        all_headlines += get_today_rss_headlines(url)

    if not all_headlines:
        send_telegram_message("❗️هیچ خبری برای تحلیل امروز یافت نشد.")
        return

    labels, stats = analyze_all(all_headlines)
    message = build_message(all_headlines, labels, stats)
    send_telegram_message(message)

if __name__ == "__main__":
    main()

