import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask

# دریافت کلیدها
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

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
        response = model.generate_content(full_prompt)
        bot.reply_to(message, response.text)
    except Exception as e:
        # این خط اضافه شد تا ارور در پنل رندر چاپ شود
        print(f"Gemini Error: {e}") 
        bot.reply_to(message, "متأسفانه مشکلی در ارتباط با هوش مصنوعی پیش آمد.")
        
# --- بخش وب‌سرور فیک برای روشن ماندن رندر ---
app = Flask(__name__)

@app.route('/')
def index():
    return "ربات امانت روشن است!"

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    # ربات در پس‌زمینه اجرا می‌شود
    threading.Thread(target=run_bot).start()
    # وب‌سرور برای رندر اجرا می‌شود
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
