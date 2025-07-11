from transformers import pipeline
from datetime import datetime

sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def classify_type(text):
    keywords = ["central bank", "interest", "inflation", "policy", "unemployment"]
    return "پایدار" if any(k in text.lower() for k in keywords) else "موقتی"

def extract_currency_pairs(text):
    pairs = {
        "EUR/USD": ["euro", "eur", "ecb"],
        "USD/JPY": ["yen", "jpy", "boj"],
        "GBP/USD": ["pound", "gbp", "boe"],
        "USD/CHF": ["swiss", "franc", "chf"],
        "AUD/USD": ["australian", "aud", "rba"],
        "USD/CAD": ["canadian", "cad", "boc"]
    }
    found = []
    for pair, keywords in pairs.items():
        if any(k in text.lower() for k in keywords):
            found.append(pair)
    return found or ["نامشخص"]

def infer_market(sentiments):
    pos = sentiments.count("positive")
    neg = sentiments.count("negative")
    if pos > neg:
        return "ریسک‌پذیر ✅"
    elif neg > pos:
        return "ریسک‌گریز ❌"
    return "متعادل ⚪️"

def analyze_sentiment(messages, title_prefix):
    sentiments = []
    currency_stats = {}

    for item in messages:
        text = item["text"]
        result = sentiment_pipeline(text)[0]
        label = result["label"].lower()
        sentiments.append(label)

        pairs = extract_currency_pairs(text)
        typ = classify_type(text)

        for pair in pairs:
            if pair not in currency_stats:
                currency_stats[pair] = {"positive": 0, "negative": 0, "type": typ}
            if label in currency_stats[pair]:
                currency_stats[pair][label] += 1

    mood = infer_market(sentiments)
    total = len(sentiments)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    parts = []
    for pair, data in currency_stats.items():
        total_pair = data["positive"] + data["negative"]
        direction = "⏫" if data["positive"] >= data["negative"] else "⏬"
        percent = round((max(data["positive"], data["negative"]) / total_pair) * 100)
        parts.append(f"{pair}{direction}{data['type']} {percent}%")

    pairs_summary = "    ".join(parts) or "نامشخص"

    return f"""{title_prefix}
⏰ تایم تحلیل: {now}
📄 تعداد پیام‌های تحلیل‌شده: {total}
📊 احساس سرمایه‌گذاران: {mood}
📈 جفت‌ارزهای تحت‌تأثیر و نوع سنتیمنت و درصد تأثیر:
{pairs_summary}
📡 تحلیل با مدل FinBERT
"""
