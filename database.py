import psycopg2
import psycopg2.errors
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DuplicateTable = psycopg2.errors.lookup("42P07")
DuplicateDatabase = psycopg2.errors.lookup('42P04')

with open('config/database.txt') as f:
    db_username = f.readline()
    db_password = f.readline()


class DBOperationalError(psycopg2.Error):
    pass


class DBOperationalSuccess(Exception):
    pass


class BotOperationalSuccess:  # TODO: really don't like it
    def __init__(self, opt=""):
        self.optional_info = opt


def init():
    query = "CREATE DATABASE urfin_users"
    open_connection(query=query, database='postgres')

    query = "CREATE TABLE list_of_all_users (username VARCHAR(255));"
    open_connection(query=query, database='urfin_users')


def open_connection(database='urfin_users', query='\\d'):  # open connection and execute command
    connection = ''
    try:
        connection = psycopg2.connect(user=db_username,
                                      password=db_password,
                                      host='localhost',
                                      port='5432',
                                      database=database)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            try:
                cursor.execute(query)
            except (DuplicateTable, DuplicateDatabase):
                return DBOperationalSuccess
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


def init_new_user(message):  # check existence of user and create table if necessary
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


def lookup(username, col, user_date):
    query = "SELECT amount, type, user_time, comment FROM {0} WHERE {1}='{2}'".format(username, col, user_date)
    return open_connection(query=query)


def lookup_month(username, col, user_date):
    query = "SELECT amount, type, day, user_time, comment FROM {0} WHERE {1}='{2}'".format(username, col, user_date)
    return open_connection(query=query)


def user_help_categories(username):
    query = "SELECT type FROM {0}".format(username)
    return open_connection(query=query)


def add(username, user, day, user_time):
    query = "INSERT INTO {0} (amount, type, day, creation_time, user_time, comment)" \
            " VALUES ({1}, '{2}', '{3}', CURRENT_TIMESTAMP, '{4}', '{5}');".format(username, user.amount,
                                                                                   user.type,
                                                                                   day,
                                                                                   user_time,
                                                                                   user.comment)
    return open_connection(query=query)
