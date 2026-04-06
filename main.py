import os
import threading
import telebot
from flask import Flask
from openai import OpenAI
from gtts import gTTS
import time

# 1. Configuration (Environment Variables se lena best hai)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8636349817:AAGz-aMhgizVSUfWxvwUxEnK6AB4zsVi-PQ")
HF_TOKEN = os.environ.get("HF_TOKEN", "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")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# openai client setup
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# 2. Voice Function
def send_voice(chat_id, text):
    try:
        # Voice file banayein (sirf pehle 250 characters ki)
        tts = gTTS(text=text[:250], lang='hi')
        tts.save("reply.mp3")
        with open("reply.mp3", "rb") as voice:
            bot.send_voice(chat_id, voice)
        os.remove("reply.mp3")
    except Exception as e:
        print(f"Voice Error: {e}")

# 3. Start Command Handler
@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    txt = f"🤖 Namaste {name}! Main Chitti hoon, main aapki kya madad kar sakta hoon boliye."
    bot.reply_to(message, txt)
    send_voice(message.chat.id, txt)

# 4. Message Handler
@bot.message_handler(func=lambda message: True)
def chat_with_bot(message):
    name = message.from_user.first_name
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", # Stable model use karein
            messages=[
                {"role": "system", "content": f"Your name is Chitti. Respond in Hinglish to {name}. 1-2 sentences."},
                {"role": "user", "content": message.text},
            ],
            max_tokens=150
        )
        
        reply = chat_completion.choices[0].message.content
        bot.reply_to(message, reply)
        
        # Voice bhejien saath mein
        bot.send_chat_action(message.chat.id, 'record_audio')
        send_voice(message.chat.id, reply)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "🤖 Maaf kijiye, system thoda busy hai.")

# 5. Flask Web Server (Render ke liye)
@app.route('/')
def index():
    return "Chitti Bot is Online!"

def run_bot():
    # Infinity polling use karein
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    # Bot thread mein chalega
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Flask main thread mein chalega (Render hamesha PORT mangta hai)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
