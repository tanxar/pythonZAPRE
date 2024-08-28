import os
import logging
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext

# Constants
TELEGRAM_TOKEN = '7542765454:AAG4dTJYB7e5N73wCfjtAcwe4bCb6bWiHdM'
WEBHOOK_URL = f'https://pythonzapre.onrender.com/{TELEGRAM_TOKEN}'

# Flask app setup
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# Handle /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Hello, World!')

# Set up webhook
def set_webhook():
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}'
    response = requests.get(url)
    print("Webhook set response:", response.json())  # Debug print

@app.route('/')
def home():
    return 'Hello, World!'

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    print("Received update:", update)  # Debug print
    application.process_update(Update.de_json(update, bot))  # Process the update
    return 'OK'

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    set_webhook()  # Set the webhook when the application starts
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
