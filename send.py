from telegram import Bot

def send_to_telegram(config, text):
    token = config["telegram_bot_token"]
    chat_id = config["telegram_target_chat_id"]
    try:
        bot = Bot(token=token)
        bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        print("خطا در ارسال پیام به تلگرام:", e)
