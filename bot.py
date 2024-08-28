import os
import psycopg2
import logging
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Telegram bot token and webhook URL
TELEGRAM_TOKEN = '7342846547:AAE4mQ4OiMmEyYYwc8SPbN1u3Cf2idfCcxw'
WEBHOOK_URL = 'https://pythonzapre.onrender.com/' + TELEGRAM_TOKEN

# PostgreSQL database URL
DATABASE_URL = 'postgresql://users_info_6gu3_user:RFH4r8MZg0bMII5ruj5Gly9fwdTLAfSV@dpg-cr6vbghu0jms73ffc840-a/users_info_6gu3'

# Flask app setup
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Handle /start command
async def start(update: Update, context: CallbackContext):
    keyboard = [['Create account'], ['Login']]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Welcome! Please choose an option:', reply_markup=reply_markup)

# Handle user responses
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    user_data = context.user_data

    if text == 'Create account':
        user_data['state'] = 'choosing_username'
        await update.message.reply_text('Please choose a username:')
    elif text == 'Login':
        user_data['state'] = 'login_username'
        await update.message.reply_text('Please enter your username:')
    elif user_data.get('state') == 'choosing_username':
        if not is_username_taken(text):
            user_data['username'] = text
            user_data['state'] = 'choosing_password'
            await update.message.reply_text('Username available. Please choose a password:')
        else:
            await update.message.reply_text('Username taken. Please choose another username:')
    elif user_data.get('state') == 'choosing_password':
        create_account(user_data['username'], text)
        await update.message.reply_text('Account created successfully!')
        user_data.clear()
        await start(update, context)
    elif user_data.get('state') == 'login_username':
        if is_username_taken(text):
            user_data['username'] = text
            user_data['state'] = 'login_password'
            await update.message.reply_text('Username found. Please enter your password:')
        else:
            await update.message.reply_text('Username does not exist. Please enter your username again:')
    elif user_data.get('state') == 'login_password':
        if verify_password(user_data['username'], text):
            await update.message.reply_text('Login successful!')
        else:
            await update.message.reply_text('Username or password incorrect. Please try again:')
        user_data.clear()
        await start(update, context)

# Helper functions for database operations
def is_username_taken(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE username = %s', (username,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def create_account(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
    conn.commit()
    cursor.close()
    conn.close()

def verify_password(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
    stored_password = cursor.fetchone()
    cursor.close()
    conn.close()
    return stored_password and stored_password[0] == password

# Set up webhook
def set_webhook():
    response = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}')
    print("Webhook set response:", response.json())  # Debug: Print the response from Telegram API

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    print("Received update:", update)  # Debug: Print the incoming update
    application.update_queue.put(Update.de_json(update, bot))
    return 'OK'

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    set_webhook()  # Set the webhook when the application starts
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
