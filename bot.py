import traceback

import telebot  # TODO: documentation
import psycopg2
import datetime


class DBOperationalSuccess(Exception):
    pass


class BotOperationalSuccess(Exception):
    pass


class DBOperationalError(psycopg2.Error):
    pass


def open_connection(database='urfin_users', query='\\d', optional=False):  # open connection and execute command
    connection = ''
    cursor = ''
    try:
        connection = psycopg2.connect(user="postgres",
                                      password='taifin',
                                      host='localhost',
                                      port='5432',
                                      database=database)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        if optional:
            return cursor.fetchall()
        else:
            raise DBOperationalSuccess
    except psycopg2.Error as Error:
        raise Error  # TODO add errors to user-named log files
    finally:
        if connection:
            cursor.close()
            connection.close()


def create_table(table_name):
    open_connection(query="CREATE TABLE {0} ("
                          "id SERIAL PRIMARY KEY NOT NULL, "
                          "amount MONEY NOT NULL,"
                          "type TEXT NOT NULL, "
                          "day DATE NOT NULL, "
                          "creation_time TIMESTAMP NOT NULL, "
                          "user_time TIME, "
                          "comment TEXT"
                          ");".format(table_name))
    open_connection(query="INSERT INTO list_of_all_users (username) '{0}'".format(table_name))


def init(message):  # check existence of user and create table if necessary
    if open_connection(query="SELECT COUNT(1) "
                             "FROM list_of_all_users "
                             "WHERE username = '{0}';".format(message.from_user.username), optional=True)[0][0] == (1,):
        raise BotOperationalSuccess
    else:
        try:
            create_table(message.from_user.username)
        except DBOperationalSuccess:
            raise BotOperationalSuccess
        except psycopg2.Error:
            raise DBOperationalError


def add(message):  # add new transaction
    # TODO: redo kek
    def bot_upd_wrapper(msg):
        print_to_user(msg, uid)
        return bot.get_updates()[0].message.text()

    bot.close()
    uid = message.from_user.id
    system_time = datetime.datetime.now()
    amount = bot_upd_wrapper("Введите сумму:")
    transaction_type = bot_upd_wrapper("Введите тип:")
    day = system_time.day
    user_time = bot_upd_wrapper("Введите примерное время или оставьте пустым:")
    comment = bot_upd_wrapper("Введите комментарий или оставьте пустым:")
    query = "INSERT INTO {0} (amount, type, day, creation_time, user_time, comment)" \
            " VALUES ({1}, {2}, {3}, {4}, {5}, {6});".format(message.from_user.id, amount, transaction_type,
                                                             day, system_time, user_time, comment)
    open_connection(query=query)


def day_lookup(message):  # return to user info from particular day
    # TODO
    pass


allowed_commands = {
    "Start": init,
    "Add": add,
    "Lookup": day_lookup
}

with open('token.txt') as f:
    token = f.readline().strip()
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=['text'])
def get_message(message):
    uid = message.from_user.id
    command = message.text
    try:
        allowed_commands[command](message)
    except DBOperationalError:
        print_to_user("Произошла ошибка работы с базами данных.", uid)
        print_to_user("Debug: " + traceback.format_exc(), uid)
    except KeyError:
        print_to_user("Неверная команда/формат, пожалуйста, проверьте справку и повторите.", uid)
    except BotOperationalSuccess:
        print_to_user("Успешно.", uid)
    except Exception as e:
        print_to_user("Debug: " + traceback.format_exc(), uid)


def print_to_user(message, uid):
    bot.send_message(uid, message)


bot.polling(none_stop=True, interval=0)
