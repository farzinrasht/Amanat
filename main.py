import os
import threading
import telebot
from openai import OpenAI
from flask import Flask

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
AVALAI_API_KEY = os.environ.get("AVALAI_API_KEY")

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

# ۱. دستور استارت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    reply_text = "سلام! به ربات «امانت» خوش آمدید. 🌸\nبرای دیدن امکانات ربات می‌توانید از منوی پایین استفاده کنید یا دستور /help را بزنید."
    user_sessions[chat_id].append({"role": "assistant", "content": reply_text})
    bot.reply_to(message, reply_text)

# ۲. دستور راهنما (Help)
@bot.message_handler(commands=['help'])
def send_help(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        user_sessions[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
    help_text = """
چطور می‌توانم کمکتان کنم؟

/start - شروع دوباره و پاک کردن حافظه مکالمه
/niyat - خالص‌سازی نیت قبل از شروع یک کار
/mohasebeh - ارزیابی و محاسبه اعمال در پایان روز
/help - نمایش همین راهنما

همچنین می‌توانید به صورت عادی با من چت کنید و از دغدغه‌های روزمره‌تان بگویید.
"""
    # راهنما نیازی به ذخیره در حافظه هوش مصنوعی ندارد چون فقط جنبه اطلاع‌رسانی دارد
    bot.reply_to(message, help_text)

# ۳. دستور نیت
@bot.message_handler(commands=['niyat'])
def handle_niyat(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        user_sessions[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
    reply_text = "بسیار عالی! چه کاری را می‌خواهی شروع کنی؟ به من بگو تا با هم بررسی کنیم چطور می‌توانیم این کار را برای رضای خدا انجام دهیم و تبدیل به عبادتش کنیم. 🌿"
    
    # اضافه کردن سوال به حافظه تا هوش مصنوعی بداند موضوع بحث چیست
    user_sessions[chat_id].append({"role": "assistant", "content": reply_text})
    bot.reply_to(message, reply_text)

# ۴. دستور محاسبه نفس
@bot.message_handler(commands=['mohasebeh'])
def handle_mohasebeh(message):
    chat_id = message.chat.id
    if chat_id not in user_sessions:
        user_sessions[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
    reply_text = """
وقت محاسبه نفس است. 🍃

امروزت چطور گذشت؟
۱. چه کار خوبی انجام دادی که بابتش شکرگزار باشی؟
۲. کجا لغزش داشتی و نیاز به استغفار داری؟
۳. به نظرت فردا رو چطور میتونی بهتر کنی؟

راحت باش و برایم بنویس تا با هم بررسی‌اش کنیم.
"""
    # ذخیره در حافظه برای درک بهتر پاسخ بعدی کاربر توسط هوش مصنوعی
    user_sessions[chat_id].append({"role": "assistant", "content": reply_text})
    bot.reply_to(message, reply_text)

# ۵. پردازش پیام‌های متنی عادی
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat_id = message.chat.id
        
        if chat_id not in user_sessions:
            user_sessions[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
            
        user_sessions[chat_id].append({"role": "user", "content": message.text})
        
        response = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=user_sessions[chat_id],
            max_tokens=2500
        )
        
        bot_reply = response.choices[0].message.content
        user_sessions[chat_id].append({"role": "assistant", "content": bot_reply})
        
        max_length = 4000
        if len(bot_reply) <= max_length:
            bot.reply_to(message, bot_reply)
        else:
            for i in range(0, len(bot_reply), max_length):
                bot.send_message(chat_id, bot_reply[i:i+max_length])
        
    except Exception as e:
        print(f"AvalAI Error: {e}", flush=True)
        bot.reply_to(message, "متأسفانه مشکلی در ارتباط با سرور پیش آمد.")

# --- وب‌سرور ---
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
