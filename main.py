import os
import telebot
import google.generativeai as genai

# دریافت کلیدها از متغیرهای محیطی (جهت حفظ امنیت)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تنظیم هوش مصنوعی Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# دستورالعمل شخصیتی ربات امانت
SYSTEM_PROMPT = """
تو یک دستیار معنوی و اسلامی به نام 'امانت' هستی.
وظیفه تو این است که فعالیت‌های روزمره کاربر را بشنوی و به او کمک کنی تا نیت خود را برای خدا خالص کند، کارهایش را به عبادت تبدیل کند و در محاسبة‌النفس به او کمک کنی.
لحن تو باید بسیار مهربان، امیدوارکننده، صمیمی و مبتنی بر آموزه‌های معنوی اسلام باشد.
"""

# ساخت نمونه ربات تلگرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "سلام! به ربات «امانت» خوش آمدید. 🌸\n\n"
        "من اینجا هستم تا در کارهای روزمره، نیت‌هایمان را برای خدا خالص‌تر کنیم "
        "و قدمی در مسیر رشد معنوی و محاسبة‌النفس برداریم.\n"
        "امروز چه کاری انجام دادی یا چه برنامه‌ای داری؟ برام بنویس."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # ترکیب پرامپت سیستم با پیام کاربر
        full_prompt = f"{SYSTEM_PROMPT}\n\nپیام کاربر: {message.text}"
        response = model.generate_content(full_prompt)
        
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "متأسفانه مشکلی در پردازش پیام پیش آمد. لطفاً مجدداً تلاش کنید.")

if __name__ == "__main__":
    print("ربات امانت روشن شد...")
    bot.polling(non_stop=True)