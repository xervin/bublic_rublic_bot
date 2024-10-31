import os
import telebot
from groq import Groq

groq_api_key = os.getenv("GROQ_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

client = Groq(api_key=groq_api_key)
bot = telebot.TeleBot(telegram_bot_token)
messages = []

@ bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global messages
    messages.append({"role": 'user', "content": message.text})
    if len(messages) > 1000:
        messages = messages[-1000:]
    response = client.chat.completions.create(model='llama-3.2-90b-vision-preview', messages=messages, temperature=0)
    bot.send_message(message.from_user.id, response.choices[0].message.content)
    messages.append({"role": 'assistant', "content": response.choices[0].message.content})

while True:
    bot.polling(none_stop=True, interval=0, timeout=0)