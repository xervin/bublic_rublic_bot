import os
import telebot
import random
from groq import Groq

groq_api_key = os.getenv("GROQ_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
first_context = os.getenv("CONTEXT")

client = Groq(api_key=groq_api_key)
bot = telebot.TeleBot(telegram_bot_token)
messages = {}

bot_info = bot.get_me()
bot_username = bot_info.username

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Здарова, бандиты!")

@bot.message_handler(commands=['reset'])
def reset_context(message):
    global messages
    chat_id = message.chat.id
    if chat_id not in messages:
          messages[chat_id] = []
    messages[chat_id] = []
    bot.reply_to(message, "Контекст сброшен")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global messages
    chat_id = message.chat.id
    username = message.from_user.username
    if chat_id not in messages:
          messages[chat_id] = []
          messages[chat_id].append({"role": 'user', "content": first_context})
          response = client.chat.completions.create(model='llama3-70b-8192', messages=messages[chat_id], temperature=0)

    print(f"Chat ID: {message.chat.id}, Username: {username}, Text: {message.text}.")
    messages[chat_id].append({"role": 'user', "content": message.text})

    response = client.chat.completions.create(model='llama3-70b-8192', messages=messages[chat_id], temperature=0)
    messages[chat_id].append({"role": 'assistant', "content": response.choices[0].message.content})

    if message.chat.type in ['group', 'supergroup']:
        if not bot_was_mentioned(message):
            rnd = random.randrange(1,100)
            if rnd > 15:
                return

    bot.send_message(message.chat.id, response.choices[0].message.content)

def bot_was_mentioned(message):
    if message.entities:
        for entity in message.entities:
            if entity.type == 'mention':
                mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                if mentioned_username.strip('@').lower() == bot_username.lower():
                    return True
    return False

while True:
    bot.polling(none_stop=True, interval=0, timeout=0)