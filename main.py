import os
import threading
import telebot
from openai import OpenAI
from flask import Flask

# دریافت کلیدها از متغیرهای محیطی رندر
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
AVALAI_API_KEY = os.environ.get("AVALAI_API_KEY")

# اتصال به سرورهای اول ای‌آی
client = OpenAI(
  base_url="https://api.avalai.ir/v1", 
  api_key=AVALAI_API_KEY,
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_sessions = {}

SYSTEM_PROMPT = """
تو یک دستیار معنوی و اسلامی به نام 'امانت' هستی.
وظیفه تو این است که فعالیت‌های روزمره کاربر را بشنوی و به او کمک کنی تا نیت خود را برای خدا خالص کند و کارهایش را به عبادت تبدیل کند.
لحن تو مهربان، امیدوارکننده و مبتنی بر آموزه‌های اسلامی باشد.
تو اجازه داری مفاهیم را به صورت عمیق و کامل توضیح دهی تا کاربر به خوبی درک کند.
"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_sessions[message.chat.id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    bot.reply_to(message, "سلام! به ربات «امانت» خوش آمدید. امروز چه برنامه‌ای داری؟")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat_id = message.chat.id
        
        # ساخت حافظه برای کاربری که تازه پیام داده
        if chat_id not in user_sessions:
            user_sessions[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
            
        user_sessions[chat_id].append({"role": "user", "content": message.text})
        
        # درخواست به سرور اول ای‌آی با مدل اقتصادی و روانِ دیپ‌سیک
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=user_sessions[chat_id],
            max_tokens=2500
        )
        
        bot_reply = response.choices[0].message.content
        user_sessions[chat_id].append({"role": "assistant", "content": bot_reply})
        
        # تکه‌تکه کردن پیام‌های طولانی برای جلوگیری از ارور تلگرام
        max_length = 4000
        if len(bot_reply) <= max_length:
            bot.reply_to(message, bot_reply)
        else:
            for i in range(0, len(bot_reply), max_length):
                bot.send_message(chat_id, bot_reply[i:i+max_length])
        
    except Exception as e:
        print(f"AvalAI Error: {e}", flush=True)
        bot.reply_to(message, "متأسفانه مشکلی در ارتباط با سرور پیش آمد.")

# --- وب‌سرور دکوری برای بیدار نگه داشتن رندر ---
app = Flask(__name__)

@app.route('/')
def index():
    return "ربات امانت (متصل به دیپ‌سیک) روشن است!"

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
