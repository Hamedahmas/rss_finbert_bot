import cloudscraper
from xml.etree import ElementTree
from transformers import pipeline
from telegram import Bot
from datetime import datetime

# تنظیمات تلگرام
TELEGRAM_TOKEN = "7685197740:AAHLS3TBygS_PBeEobf9fyYKQy6M5rANl6s"
TELEGRAM_CHAT_ID = "-1002764995883"

# مدل FinBERT
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# لیست RSS کانال‌ها
RSS_URLS = [
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

# کلمات کلیدی جفت ارز
CURRENCY_KEYWORDS = {
    "EUR/USD": ["eur", "euro", "ecb"],
    "USD/JPY": ["jpy", "yen", "boj"],
    "GBP/USD": ["gbp", "pound", "boe"],
    "USD/CHF": ["chf", "swiss", "franc"],
    "AUD/USD": ["aud", "australian", "rba"],
    "USD/CAD": ["cad", "canadian", "boc"],
}

# کلیدواژه‌های پایدار
STABLE_KEYWORDS = ["interest rate", "inflation", "central bank", "policy", "GDP", "unemployment", "ecb", "fed", "boj"]

def fetch_rss_titles():
    scraper = cloudscraper.create_scraper()
    titles = []
    for url in RSS_URLS:
        try:
            res = scraper.get(url, timeout=10)
            root = ElementTree.fromstring(res.text)
            for item in root.findall(".//item"):
                title = item.find("title").text.strip()
                titles.append(title)
        except Exception as e:
            print(f"خطا در دریافت RSS {url}: {e}")
    return titles

def analyze_sentiment(texts):
    return sentiment_pipeline(texts, truncation=True)

def classify_sentiment(results):
    counter = {"positive": 0, "neutral": 0, "negative": 0}
    for r in results:
        label = r['label'].lower()
        if label in counter:
            counter[label] += 1
    total = sum(counter.values())
    top = max(counter, key=counter.get)
    mood = {"positive": "صعودی ✅", "negative": "نزولی ❌", "neutral": "دارایی های امن ⚪️"}.get(top, "نامشخص ❓")
    return mood, total

def extract_currency_impact(titles, results):
    impact = {}
    for title, sentiment in zip(titles, results):
        text = title.lower()
        label = sentiment["label"].lower()
        type_ = "پایدار" if any(k in text for k in STABLE_KEYWORDS) else "موقتی"
        for pair, keys in CURRENCY_KEYWORDS.items():
            if any(k in text for k in keys):
                if pair not in impact:
                    impact[pair] = {"positive": 0, "negative": 0, "neutral": 0, "type": type_}
                impact[pair][label] += 1
    summary = []
    for pair, data in impact.items():
        total = sum(data.values()) - (1 if "type" in data else 0)
        main = max(["positive", "negative", "neutral"], key=lambda x: data[x])
        sign = {"positive": "⏫", "negative": "⏬", "neutral": "⚪️"}[main]
        percent = int((data[main] / total) * 100) if total else 0
        summary.append(f"{pair} {sign} {data['type']} {percent}%")
    return summary

def build_message(titles, sentiments):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    title = titles[0] if titles else "عنوانی یافت نشد"
    mood, total = classify_sentiment(sentiments)
    pairs = extract_currency_impact(titles, sentiments)
    return f"""⏰ تایم اخبار: {now}

📰 عنوان: {title}

📄 تعداد خبرهای تحلیل شده: {total}

📊 احساس سرمایه گذارها و تریدرها نسبت به بازار: {mood}

📈 جفت‌ارزهای تحت‌تأثیر و نوع سنتیمنت و درصد تأثیر:
{chr(10).join(pairs)}

📡 تحلیل اتوماتیک با هوش مصنوعی | بروزرسانی هر ۳۰ دقیقه"""

def send_telegram_message(text):
    try:
        Bot(token=TELEGRAM_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print("خطا در ارسال پیام:", e)

def main():
    titles = fetch_rss_titles()
    if not titles:
        send_telegram_message("⛔️ خبری برای تحلیل یافت نشد.")
        return
    sentiments = analyze_sentiment(titles)
    message = build_message(titles, sentiments)
    send_telegram_message(message)

if __name__ == "__main__":
    main()
