from fetch import fetch_all_messages
from analyze import analyze_sentiment
from send import send_to_telegram
import json

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    config = load_config()

    all_messages = fetch_all_messages(config)
    if not all_messages:
        send_to_telegram(config, "⛔️ هیچ پیامی برای تحلیل یافت نشد.")
        return

    full_report = analyze_sentiment(all_messages, "🟢 تحلیل همه پیام‌ها")
    send_to_telegram(config, full_report)

    from datetime import datetime
    today = datetime.utcnow().date()
    todays_messages = [m for m in all_messages if m["date"].date() == today]

    if todays_messages:
        daily_report = analyze_sentiment(todays_messages, "🔵 تحلیل پیام‌های امروز")
        send_to_telegram(config, daily_report)
    else:
        send_to_telegram(config, "❗️هیچ پیام امروزی یافت نشد.")

if __name__ == "__main__":
    main()
