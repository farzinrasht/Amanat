import os
import threading
import telebot
from openai import OpenAI
from flask import Flask

# دریافت کلیدها از تنظیمات رندر
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# اتصال به سرورهای OpenRouter با استفاده از کتابخانه OpenAI
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

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
        # ارسال پیام به OpenRouter
        response = client.chat.completions.create(
            # نام مدل جدید انویدیا دقیقاً در اینجا قرار می‌گیرد
            model="nvidia/nemotron-3-ultra-550b-a55b:free", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        
        # استخراج و ارسال پاسخ به کاربر
        bot_reply = response.choices[0].message.content
        bot.reply_to(message, bot_reply)
        
    except Exception as e:
        print(f"OpenRouter Error: {e}", flush=True)
        bot.reply_to(message, "متأسفانه مشکلی در ارتباط با هوش مصنوعی پیش آمد.")

# --- بخش وب‌سرور فیک برای روشن ماندن رندر ---
app = Flask(__name__)

@app.route('/')
def index():
    return "ربات امانت (نسخه OpenRouter) روشن است!"

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
