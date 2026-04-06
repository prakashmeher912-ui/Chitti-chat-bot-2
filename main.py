import os
import threading
import telebot
from flask import Flask
from openai import OpenAI

# 1. Fetch Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not BOT_TOKEN or not HF_TOKEN:
    raise ValueError("BOT_TOKEN and HF_TOKEN must be set in environment variables.")

# 2. Initialize Telegram Bot and Flask App
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 3. Initialize OpenAI Client (Pointed to Hugging Face router)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# 4. Telegram Bot Message Handler
@bot.message_handler(func=lambda message: True)
def chat_with_bot(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Call the Hugging Face model using OpenAI SDK syntax
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2-Exp:novita",
            messages=[
                {
                    "role": "user",
                    "content": message.text,
                },
            ],
        )
        
        # Extract the reply and send it back to the user
        reply = chat_completion.choices[0].message.content
        bot.reply_to(message, reply)

    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        bot.reply_to(message, error_msg)
        print(error_msg)

# 5. Flask Web Server Route (Required for Render to keep the app alive)
@app.route('/')
def index():
    return "Telegram Bot is running smoothly on Render!"

# 6. Run Bot in a Background Thread
def run_bot():
    print("Starting Telegram Bot...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Start the bot thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Start the Flask web server
    # Render assigns a port dynamically via the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port)
