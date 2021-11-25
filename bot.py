import sys
from telegram import Update
from telegram.ext import Updater, MessageHandler, CallbackContext, Filters, CommandHandler, ConversationHandler
import psycopg2
import psycopg2.errors
import datetime
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

DuplicateTable = psycopg2.errors.lookup("42P07")

if sys.platform == 'linux':
    password = 'postgres'
else:
    password = 'taifin'

TYPING_AMOUNT, TYPING_TYPE, TYPING_TIME, TYPING_COMMENT = range(4)
GET_DATE = 0

users = {}  # TODO: bad idea


class DBOperationalSuccess(Exception):
    pass


class BotOperationalSuccess:
    def __init__(self, opt=""):
        self.optional_info = opt


class DBOperationalError(psycopg2.Error):
    pass


class UserNewAdd:
    def __init__(self):
        self.amount = 0
        self.type = ""
        self.time = "00:00"
        self.comment = ""


def open_connection(database='urfin_users', query='\\d'):  # open connection and execute command
    connection = ''
    try:
        connection = psycopg2.connect(user="postgres",
                                      password=password,
                                      host='localhost',
                                      port='5432',
                                      database=database)
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
            except DuplicateTable:
                raise DBOperationalSuccess
            connection.commit()
            try:
                return cursor.fetchall()
            except psycopg2.ProgrammingError:
                return
    except psycopg2.Error as Error:
        raise Error  # TODO add errors to user-named log files
    finally:
        if connection:
            connection.close()


def create_table(table_name):
    open_connection(query="CREATE TABLE {0} ("
                          "id SERIAL PRIMARY KEY NOT NULL, "
                          "amount MONEY NOT NULL,"
                          "type TEXT NOT NULL, "
                          "day DATE NOT NULL, "
                          "creation_time TIMESTAMP NOT NULL, "
                          "user_time TIMESTAMP, "
                          "comment TEXT"
                          ");".format(table_name))
    return open_connection(query="INSERT INTO list_of_all_users (username) '{0}'".format(table_name))


def init(message):  # check existence of user and create table if necessary
    query = """SELECT COUNT(1) 
                FROM list_of_all_users 
                WHERE username = '{0}';
            """.format(message)
    try:
        open_connection(query=query)
        return BotOperationalSuccess("Table already exists!")
    except DBOperationalSuccess:
        try:
            if create_table(message):
                return BotOperationalSuccess("Table successfully created!")
        except psycopg2.Error:
            raise DBOperationalError


def day_lookup(username, day):
    query = "SELECT amount, type, user_time, comment FROM {0} WHERE day='{1}'".format(username, day)
    return open_connection(query=query)


def parse_date(date):
    now = datetime.datetime.now()
    if len(date) <= 2:
        real_date = str(now.year) + '-' + str(now.month) + '-' + date
        return real_date
    for fmt in ("%Y-%m-%d", "%Y %m %d", "%Y.%m.%d", "%Y,%m,%d", "%Y\\%m\\%d", "%Y/%m/%d"):
        try:
            formatted = datetime.datetime.strptime(date, fmt)
            print(formatted)
            return formatted.strftime("%Y-%m-%d")
        except ValueError:
            pass


def bot_day_lookup(update: Update, context: CallbackContext):  # return to user info from particular day
    # TODO: add option to merge data into a table?
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please, enter the date you want to get "
                                                                    "information on. You can enter the date in two "
                                                                    "ways: a single or two digits meaning day of "
                                                                    "current month or full date, including year, "
                                                                    "month and day (please, mind the separators, "
                                                                    "such as ',', '.', ' ', '/', '\\', '-').")

    return GET_DATE


def bot_receive_date(update: Update, context: CallbackContext):
    user_date = parse_date(update.message.text)
    data = day_lookup(update.message.from_user.username, user_date)
    print(data)  # debug
    if not data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hm... It seems that there's no data from "
                                                                        "specified day, please, try again!")
        # TODO: suggest finding closest (all?) days
    else:
        response = ''
        for row in data:
            response += 'Spent {0} on {1} at {2}, your comment: {3}\n'.format(row[0], row[1],
                                                                              row[2].strftime("%I:%M:%S"), row[3])
        context.bot.send_message(chat_id=update.effective_chat.id, text="Here's what I found!:\n" + response)
    return ConversationHandler.END


def category_lookup():
    # TODO
    pass


def bot_start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Checking if there's already a table for you.")
    try:
        init(update.effective_user.username)
    except BotOperationalSuccess as res:
        context.bot.send_message(chat_id=update.effective_chat.id, text=res.optional_info)


def bot_help(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Allowed commands:\n"
                                                                    "/start - use this command if you are a new user\n"
                                                                    "/add - initiate process of adding new "
                                                                    "transaction\n"
                                                                    "/add_inline - initiate process of adding new"
                                                                    "transaction in a single line\n"
                                                                    "/addhelp - show tips for using 'add' command\n"
                                                                    "/daylookup - get info on particular day\n"
                                                                    "/help - well, don't you know what's that for???")


def bot_add_inline(update: Update, context: CallbackContext):
    msg = update.message.text.split('  ')
    amount = msg[0]
    transaction_type = msg[1].join(' ')
    user_time = msg[2]
    comment = msg[3].join(' ')
    day = str(datetime.datetime.now().day) + '.' + str(datetime.datetime.now().month)
    system_time = datetime.datetime.now()

    context.bot.send_message(chat_id=update.effective_chat.id, text="Trying to add your record into database.")
    query = "INSERT INTO {0} (amount, type, day, creation_time, user_time, comment)" \
            " VALUES ({1}, '{2}', '{3}', '{4}', '{5}', '{6}');".format(update.effective_user.id, amount,
                                                                       transaction_type,
                                                                       day, system_time, user_time, comment)
    try:
        open_connection(query=query)
    except BotOperationalSuccess as res:
        context.bot.send_message(chat_id=update.effective_chat.id, text=res.optional_info)


def bot_add(update: Update, context: CallbackContext):
    users[update.effective_user.username] = UserNewAdd()
    context.bot.send_message(chat_id=update.effective_chat.id, text="Arrrr, you want to log some wasted money? "
                                                                    "Please tell me how much.")

    return TYPING_AMOUNT


def bot_receive_amount(update: Update, context: CallbackContext):
    amount = update.message.text
    update.message.reply_text("W-w-wonderful! Going next: what was the type of the spending?")
    users[update.effective_user.username].amount = amount

    return TYPING_TYPE


def bot_receive_type(update: Update, context: CallbackContext):
    transaction_type = update.message.text.lower()
    users[update.effective_user.username].type = transaction_type
    context.bot.send_message(chat_id=update.effective_chat.id, text="Now let's talk about time. If you remember "
                                                                    "approximate time of your spending, enter it "
                                                                    "in "
                                                                    "format of 'hh:mm'.")

    return TYPING_TIME


def bot_receive_time(update: Update, context: CallbackContext):
    user_time = update.message.text
    users[update.effective_user.username].time = user_time
    context.bot.send_message(chat_id=update.effective_chat.id, text="Any commentaries? Leave blank if no.")

    return TYPING_COMMENT


def bot_receive_comment(update: Update, context: CallbackContext):
    comment = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Okay, everything is set up, now I'm trying to "
                                                                    "add your record into database.")
    users[update.effective_user.username].comment = comment

    user = users[update.effective_user.username]
    now = datetime.datetime.now()

    query = "INSERT INTO {0} (amount, type, day, creation_time, user_time, comment)" \
            " VALUES ({1}, '{2}', '{3}', '{4}', '{5}', '{6}');".format(update.effective_user.username, user.amount,
                                                                       user.type,
                                                                       str(now.year) +
                                                                       str(now.month) + str(now.month),
                                                                       datetime.datetime.now().strftime(
                                                                           '%Y-%m-%d %H:%M:%S'),
                                                                       datetime.datetime(now.year, now.month,
                                                                                         day=now.day,
                                                                                         hour=int(user.time[:2]),
                                                                                         minute=int(
                                                                                             user.time[3:])).strftime(
                                                                           '%Y-%m-%d %H:%M:%S'),
                                                                       user.comment)
    open_connection(query=query)

    return ConversationHandler.END


def bot_message(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Sorry, but I'm a bit stupid and I understand "
                                                                    "only certain commands, that you can check by "
                                                                    "asking me for help by '/help'.")


def bot_addhelp(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Okay, here's what's you need to know before use '/add' command:\n"
                                  "If you are asked of transaction cost, please, send it in format of single line of "
                                  "numbers\n"
                                  "If you need to send me type of transaction, "
                                  "feel free to type anything you want\n"
                                  "When the time is asked, I will give you advice on that\n"
                                  "Commentary is also can be anything you want!\n"
                                  "Furthermore, you can add your transaction in single-line ('/add_inline'), but the "
                                  "format is very strict (for now):\n"
                                  "NOTE THAT SEPARATION IS TWO WHITESPACES\n"
                                  "COST(line of numbers)  TYPE(line of words)  TIME(hh:mm)  COMMENT(line of words)")


if __name__ == "__main__":
    with open('token.txt') as f:
        token = f.readline().strip()
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', bot_start))
    dispatcher.add_handler(CommandHandler('help', bot_help))
    dispatcher.add_handler(CommandHandler('addhelp', bot_addhelp))
    add_conv = ConversationHandler(entry_points=[CommandHandler('add', bot_add)],
                                   states={
                                       TYPING_AMOUNT: [
                                           MessageHandler(Filters.all,
                                                          bot_receive_amount)],
                                       TYPING_TYPE: [
                                           MessageHandler(Filters.text & (~Filters.command), bot_receive_type)],
                                       TYPING_TIME: [
                                           MessageHandler(
                                               Filters.text & (~Filters.command) & Filters.regex('\d\d:\d\d'),
                                               bot_receive_time)],
                                       TYPING_COMMENT: [
                                           MessageHandler(Filters.text & (~Filters.command), bot_receive_comment)]},
                                   fallbacks=[MessageHandler(~Filters.command, bot_message)])
    day_lookup_conv = ConversationHandler(entry_points=[CommandHandler('daylookup', bot_day_lookup)],
                                          states={
                                              GET_DATE: [
                                                  MessageHandler(Filters.text & (~Filters.command), bot_receive_date)]},
                                          # TODO: regex for date
                                          fallbacks=[MessageHandler(~Filters.command, bot_message)])
    dispatcher.add_handler(add_conv)
    dispatcher.add_handler(day_lookup_conv)
    updater.start_polling()
    updater.idle()
