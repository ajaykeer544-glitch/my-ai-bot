import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

# Render को एक्टिव रखने के लिए छोटा वेब सर्वर
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is Running 24/7!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# क्लाउड से चाबियां उठाना
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)
user_chat_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_chat_sessions[user_id] = ai_client.chats.create(model="gemini-2.5-flash")
    await update.message.reply_text("हेलो! मैं आपका 24 घंटे चालू रहने वाला AI असिस्टेंट हूँ। पूछिए क्या पूछना है?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    try:
        if user_id not in user_chat_sessions:
            user_chat_sessions[user_id] = ai_client.chats.create(model="gemini-2.5-flash")
        chat = user_chat_sessions[user_id]
        response = chat.send_message(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("कुछ दिक्कत आ रही है भाई, थोड़ा रुक कर कोशिश करें।")

def main():
    Thread(target=run_flask).start()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
  
