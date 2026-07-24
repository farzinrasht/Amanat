import os
import threading
import telebot
from google import genai
from flask import Flask

# دریافت کلیدها
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# اتصال به کلاینت جدید گوگل
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
تو یک دستیار معنوی و اسلامی به نام 'امانت' هستی.
وظیفه تو این است که فعالیت‌های روزمره کاربر را بشنوی و به او کمک کنی تا نیت خود را برای خدا خالص کند و کارهایش را به عبادت تبدیل کند.
لحن تو مهربان، امیدوارکننده و مبتنی بر آموزه‌های اسلامی باشد.
"""

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به ربات «امانت» خوش آمدید. امروز چه برنامه‌ای داری؟")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nپیام کاربر: {message.text}"
        
        # استفاده از متد جدید گوگل برای دریافت پاسخ
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=full_prompt,
        )
        
        bot.reply_to(message, response.text)
    except Exception as e:
        # استفاده از flush برای چاپ فوری خطا در صورت بروز مشکل مجدد
        print(f"Gemini Error: {e}", flush=True) 
        bot.reply_to(message, "متأسفانه مشکلی در ارتباط با هوش مصنوعی پیش آمد.")

# --- بخش وب‌سرور فیک برای روشن ماندن رندر ---
app = Flask(__name__)

@app.route('/')
def index():
    return "ربات امانت روشن است!"

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
