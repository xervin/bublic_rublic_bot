import os
import time
import telebot
import random
from groq import Groq

groq_api_key = os.getenv("GROQ_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
first_context = os.getenv("CONTEXT")
model = os.getenv("MODEL")

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
    messages[chat_id] = [{"role": 'user', "content": first_context}]
    bot.reply_to(message, "Контекст сброшен")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global messages
    chat_id = message.chat.id
    username = message.from_user.username

    if chat_id not in messages:
        messages[chat_id] = []
        messages[chat_id].append({"role": 'user', "content": first_context})
        # Попытка установить контекст с моделью
        try:
            response = client.chat.completions.create(model=model, messages=messages[chat_id], temperature=0)
        except Exception as e:
            print(f"Ошибка при установлении контекста: {str(e)}")
            bot.send_message(chat_id, "Произошла ошибка при установлении контекста. Пожалуйста, попробуйте позже.")
            return

    if message.chat.type in ['group', 'supergroup']:
        if not bot_was_mentioned(message):
            rnd = random.randrange(1, 100)
            if rnd > 25:
                return

    print(f"Chat ID: {chat_id}, Username: {username}, Text: {message.text}.")
    messages[chat_id].append({"role": 'user', "content": message.text})

    try:
        response = client.chat.completions.create(model=model, messages=messages[chat_id], temperature=0)
        assistant_reply = response.choices[0].message.content
        messages[chat_id].append({"role": 'assistant', "content": assistant_reply})
        bot.send_message(chat_id, assistant_reply)
    except Exception as e:
        print(f"Ошибка при получении ответа от модели: {str(e)}")
        bot.send_message(chat_id, "Произошла ошибка при получении ответа от модели. Пожалуйста, попробуйте позже.")

def bot_was_mentioned(message):
    if message.entities:
        for entity in message.entities:
            if entity.type == 'mention':
                mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                if mentioned_username.strip('@').lower() == bot_username.lower():
                    return True
    return False

while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=0)
    except Exception as e:
        print(f"Ошибка при работе бота: {str(e)}")
        time.sleep(15)