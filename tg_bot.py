import conf
import telebot
import flask
import json
import requests



def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.BOT_TOKEN)

headers = {"Authorization": f"Bearer {conf.API_TOKEN}"}
API_URL = "https://api-inference.huggingface.co/models/efromomr/rugpt3small_based_on_gpt2-tat_model"
bot = telebot.TeleBot(conf.BOT_TOKEN, threaded = False)  # создаем экземпляр бота


# удаляем старые вебхуки
bot.remove_webhook()

# ставим новые
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

# реагируем на команды /start и /help
@bot.message_handler(commands=['start', 'help'])
def help(message):
    user = message.chat.id
    bot.send_message(user, "Привет, зай! Напиши что-нибудь, а я продолжу.")

# content_types=['text'] - сработает, если нам прислали текстовое сообщение
@bot.message_handler(content_types=['text'])
def echo(message):
    text = message.text
    user = message.chat.id

    data = query({
    "inputs": text,
    'parameters': {'max_new_tokens': 250, 'top_k': 50, 'top_p': 0.95, 'do_sample': True},
    'options': {'wait_for_model': True, 'use_cache': False}
    })
    answer = data[0]['generated_text']
    answer = answer[:answer.rfind('.')+1] #обрезаем до последней точки



    bot.send_message(user, answer)



# главная страница
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)