import telebot
import psycopg2

with open('token.txt') as f:
    token = f.readline().strip()
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=['text'])
def get_message(message):
    # switch-case operator can be implemented with dictionary
    uid = message.from_user.id
    if message.text in ['Hi', 'Hello', 'Privet', 'Привет']:
        print_to_user("Приветик!", uid)
    elif message.text == 'Start':
        username = message.from_user.username
        print_to_user("Делаю табличечку!", uid)
        print_to_user(new_user_initialization(username), uid)
    else:
        print_to_user("Ну пока. :(", uid)


def print_to_user(message, uid):
    bot.send_message(uid, message)


def new_user_initialization(username):
    try:
        connection = psycopg2.connect(user="postgres",
                                      password='taifin',
                                      host='localhost',
                                      port='5432',
                                      database='urfin_users')
        cursor = connection.cursor()
        table_to_create = 'CREATE TABLE ' + username + """
        (id BIGSERIAL PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        datetime TIMESTAMP NOT NULL,
        comment TEXT);
        """
        cursor.execute(table_to_create)
        connection.commit()
        return "Создание таблицы прошло успешно!"
    except (Exception, psycopg2.Error) as Error:
        return Error
    finally:
        if connection:
            cursor.close()
            connection.close()
            return 'Соединение закрыто'


def new_transaction(name, datetime, username, comment=""):
    try:
        connection = psycopg2.connect(user="postgres",
                                      password='taifin',
                                      host='localhost',
                                      port='5432',
                                      database='urfin_users')
        cursor = connection.cursor()
        query = "INSERT INTO " + username + "(name, datetime, comment) values ( " \
                + name + ' ' + datetime + ' ' + comment + ');'
        cursor.execute(query)
        connection.commit()
        return "Успешно добавил транзакцию."
    except (Exception, psycopg2.Error) as Error:
        return Error
    finally:
        if connection:
            cursor.close()
            connection.close()
            return 'Соединение закрыто'


bot.polling(none_stop=True, interval=0)
