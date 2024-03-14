import json
import subprocess
import time
from datetime import datetime
import requests
import json
import telebot
import configparser

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
'''
[settings]
token_chatgtp = *******
chat_id = *******
token_telegram = *******
message_id = *******
'''

token_telegram = (config["settings"]["token_telegram"])
chatID = (config["settings"]["chat_id"])

token_telegram = telebot.TeleBot(token_telegram)
chatID = telebot.TeleBot(chatID)

  

request_url = requests.get('https://api.telegram.org/bot{}/getUpdates'.format(token_telegram)).json()

try:
    chat_id = int(request_url['result'][0]['my_chat_member']['chat']['id'])
except:
    chat_id = int(request_url['result'][0]['message']['chat']['id'])

bot = telebot.TeleBot(token_telegram)

# количество постов
iii = 2
def load_post():
    # парсит данные
    cmd_str = 'snscrape --max-results {} --jsonl telegram-channel nastolka_n1 > ss.txt'.format(iii + 1)
    subprocess.run(cmd_str, shell=True)
    db = []
    # основной окд
    with open('ss.txt') as datas:
        for i, data in enumerate(datas):  # проходит по списку
            index = json.loads(data)

            # дата
            date = index['date'].split(('T', 1)[0])[0]

            # время
            date_time = index['date'].split('T', 1)[1]
            time = date_time[:str(date_time).find('+')]

            content = str(index['content'])
            db.append(content)
    return db


# удаляем не нужные посты
def check_post(posts):
    res = []
    for post in posts:
        if post.find('🏓Сигнал') >= 0:
            res.append(post)
    return res


def check_new_post(posts):
    post = posts[0]
    if post.find("❌") == -1 and post.find("✅") == -1:
        return True
    else:
        return False


def check_3_post(posts, iii):
    res = 0
    for post in posts:
        if post.find("❌") >= 0:
            res += 1
    if res == iii:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def main(iii,chatID):

    try:
        post_ini = 0
        post_message = ''
        for i in range(0, 10000):
            print(post_ini, datetime.now().strftime("%H:%M:%S"))

            try:
                load_text = load_post()

                # load_text = [
                #     '🏓Сигнал #19122Настольный теннис. Лига ПроВремя матча: скоро начнется...Александр Клавденков (Рос) ‑ Дмитрий Богатов (Рос)Ставка:  Дмитрий Богатов (Рос) ИТМ <9.5 кф 1.83Как ставить? '
                #     'ЧИТАЙ ЗАКРЕП!!!',
                #     '🏓Сигнал #19121Настольный теннис. Лига ПроВремя матча: скоро начнется...Владимир Пустоселов (Рос) ‑ Евгений Воронков (Рос)Ставка:  Евгений Воронков (Рос) ИТМ <9.5 кф 1.86Как ставить? '
                #     'ЧИТАЙ ЗАКРЕП!!!❌  1 сет (11-6) (11-9)']

                posts = (check_post(load_text))  # удаляем не нужные посты
                post = posts[0]


                # проверяем последний пост, он новый или нет
                if check_new_post(posts):
                    if post_message != post:
                        post_message = post

                    # проверяем 3 последних поста на наличия проигрыша ❌
                    if check_3_post(posts, iii):
                        # номер
                        nomber = int(post[:post.find('Настольный')].replace('🏓Сигнал ', '').replace('#', '').strip())
                        print(nomber)

                        if post_ini < nomber:
                            mes = post[9:].replace('Как ставить? ЧИТАЙ ЗАКРЕП!!!','')
                            apiReq = "https://api.telegram.org/bot" + token_telegram + "/sendMessage?chat_id=" + chatID + "&text={}".format(mes)
                            requests.get(apiReq).json()
                            print('Отправка сообщения: {}'.format(mes))
                            post_ini = nomber
                    else:
                        pass
                else:
                    pass
            except Exception as err:
                print('Ошибка: {}'.format(err))

            time.sleep(5)

    except Exception as error:
        print('Ошибка {}'.format(error))
    bot.infinity_polling()


if __name__ in "__main__":
    main(iii,chatID)
