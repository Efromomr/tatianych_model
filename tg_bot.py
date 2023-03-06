# coding: utf-8

import conf
import telebot
import json
import requests

def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

headers = {"Authorization": f"Bearer {conf.API_TOKEN}"}
API_URL = "https://api-inference.huggingface.co/models/efromomr/rugpt3small_based_on_gpt2-tat_model"
bot = telebot.TeleBot(conf.TOKEN)  # создаем экземпляр бота

# реагируем на команды /start и /help
@bot.message_handler(commands=['start', 'help'])
def help(message):
    user = message.chat.id
    bot.send_message(user, "Привет, зай! Напиши что-нибудь, а я продолжу.")

# content_types=['text'] - сработает, если нам прислали текстовое сообщение
@bot.message_handler(content_types=['text'])
def echo(message):
    # message - входящее сообщение
    # message.text - это его текст
    # message.chat.id - это номер его автора
    text = message.text
    user = message.chat.id
    
    data = query({
    "inputs": text, 
    'parameters': {'max_new_tokens': 250, 'top_k': 50, 'top_p': 0.95, 'do_sample': True},
    'options': {'wait_for_model': True, 'use_cache': False}
    })
    answer = data[0]['generated_text']
    answer = answer[:answer.rfind('.')+1] #обрезаем до последней точки
    


    #отправляем сообщение тому же пользователю с тем же текстом
    bot.send_message(user, answer)

# поллинг - вечный цикл с обновлением входящих сообщений
bot.polling(none_stop=True)

#'repetition_penalty': 100.0,