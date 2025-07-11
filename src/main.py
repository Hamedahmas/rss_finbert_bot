from transformers import pipeline
from telegram import Bot
from datetime import datetime
from utils import get_rss_entries, is_today

TELEGRAM_TOKEN = "7685197740:AAHLS3TBygS_PBeEobf9fyYKQy6M5rANl6s"
TELEGRAM_CHAT_ID = "-1002764995883"

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

sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def extract_currency_info(title):
    pairs = {
        "EUR/USD": ["eur", "euro", "ecb"],
        "USD/JPY": ["jpy", "yen", "boj"],
        "GBP/USD": ["gbp", "pound", "boe"],
        "USD/CHF": ["chf", "franc"],
        "AUD/USD": ["aud", "australian", "rba"],
        "USD/CAD": ["cad", "canadian", "boc"]
    }
    result = []
    for pair, keys in pairs.items():
        for key in keys:
            if key in title.lower():
                result.append(pair)
                break
    return result

def classify_type(title):
    keywords = ["central bank", "interest", "inflation", "policy", "unemployment"]
    for word in keywords:
        if word in title.lower():
            return "پایدار"
    return "موقتی"

def infer_market(sentiments):
    positive = sum(1 for s in sentiments if s == "positive")
    negative = sum(1 for s in sentiments if s == "negative")
    if positive > negative:
        return "ریسک‌پذیر ✅"
    elif negative > positive:
        return "ریسک‌گریز ❌"
    else:
        return "متعادل ⚪️"

def analyze(entries, title_prefix):
    sentiments = []
    currency_stats = {}

    for item in entries:
        title = item["title"]
        result = sentiment_pipeline(title)[0]
        label = result["label"].lower()
        sentiments.append(label)

        for pair in extract_currency_info(title):
            if pair not in currency_stats:
                currency_stats[pair] = {"positive": 0, "negative": 0, "type": classify_type(title)}
            currency_stats[pair][label] += 1

    market_mood = infer_market(sentiments)
    total = len(sentiments)

    currencies_output = ""
    for pair, data in currency_stats.items():
        total_pair = data["positive"] + data["negative"]
        direction = "⏫" if data["positive"] > data["negative"] else "⏬"
        percent = round((max(data["positive"], data["negative"]) / total_pair) * 100)
        type_ = data["type"]
        currencies_output += f"{pair}{direction}{type_} {percent}%   "

    titles_list = [e["title"] for e in entries[:3]]
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return f"""
📌 {title_prefix}
⏰ تایم تحلیل: {now_str}
📰 عناوین نمونه: {' ؛ '.join(titles_list)}
📄 تعداد خبرهای تحلیل‌شده: {total}
📊 احساس سرمایه‌گذاران: {market_mood}
📈 جفت‌ارزهای تأثیرگرفته: {currencies_output}
📡 تحلیل با مدل FinBERT
"""

def send_telegram(text):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)

def main():
    entries = get_rss_entries(RSS_FEEDS)

    if not entries:
        send_telegram("⛔️ هیچ خبری دریافت نشد.")
        return

    all_message = analyze(entries, "🟢 تحلیل کلی (تمامی اخبار)")
    send_telegram(all_message)

    today_entries = [e for e in entries if is_today(e.get("published", ""))]
    if today_entries:
        today_message = analyze(today_entries, "🔵 تحلیل خبرهای امروز")
        send_telegram(today_message)
    else:
        send_telegram("❗️هیچ خبری برای امروز یافت نشد.")

if __name__ == "__main__":
    main()
