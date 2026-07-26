import os
import threading
import telebot
from google import genai
from google.genai import types
from flask import Flask

# دریافت کلید تلگرام و گوگل
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# یک دیکشنری برای نگهداری حافظه چتِ هر کاربر به صورت مجزا
user_sessions = {}

# پرامپت آپدیت شده: حذف محدودیت کلمات و اجازه برای توضیحات عمیق‌تر
SYSTEM_PROMPT = """
تو یک دستیار معنوی و اسلامی به نام 'امانت' هستی.
وظیفه تو این است که فعالیت‌های روزمره کاربر را بشنوی و به او کمک کنی تا نیت خود را برای خدا خالص کند و کارهایش را به عبادت تبدیل کند.
لحن تو مهربان، امیدوارکننده و مبتنی بر آموزه‌های اسلامی باشد.
تو اجازه داری مفاهیم را به صورت عمیق و کامل توضیح دهی تا کاربر به خوبی درک کند.
"""

def get_or_create_chat(chat_id):
    # اگر کاربر قبلاً چت نکرده بود یا حافظه‌اش پاک شده بود، یک نشست جدید بساز
    if chat_id not in user_sessions:
        user_sessions[chat_id] = client.chats.create(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                # افزایش سقف خروجی برای اجازه دادن به تولید متن‌های طولانی (حدود ۲ تا ۳ پیام تلگرامی)
                max_output_tokens=2500,
            )
        )
    return user_sessions[chat_id]

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # وقتی کاربر /start را می‌زند، حافظه قبلی او ریست می‌شود تا چت را از نو شروع کند
    user_sessions[message.chat.id] = client.chats.create(
        model='gemini-2.0-flash',
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=2500,
        )
    )
    bot.reply_to(message, "سلام! به ربات «امانت» خوش آمدید. امروز چه برنامه‌ای داری؟")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # فراخوانی چت اختصاصی این کاربر (که پیام‌های قبلی را به یاد دارد)
        chat_session = get_or_create_chat(message.chat.id)
        
        # ارسال پیام جدید به نشست چت
        response = chat_session.send_message(message.text)
        bot_reply = response.text
        
        # مدیریت هوشمند پیام‌های طولانی برای تلگرام (برش در صورت عبور از ۴۰۰۰ کاراکتر)
        max_length = 4000
        if len(bot_reply) <= max_length:
            bot.reply_to(message, bot_reply)
        else:
            for i in range(0, len(bot_reply), max_length):
                bot.send_message(message.chat.id, bot_reply[i:i+max_length])
        
    except Exception as e:
        print(f"Gemini Error: {e}", flush=True)
        bot.reply_to(message, "متأسفانه مشکلی در ارتباط با هوش مصنوعی پیش آمد.")

# --- بخش وب‌سرور برای روشن ماندن رندر ---
app = Flask(__name__)

@app.route('/')
def index():
    return "ربات امانت (نسخه حافظه‌دار جمینای) روشن است!"

def run_bot():
    bot.polling(non_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
