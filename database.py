import psycopg2
import psycopg2.errors
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DuplicateTable = psycopg2.errors.lookup("42P07")
DuplicateDatabase = psycopg2.errors.lookup('42P04')

with open('config/database.txt') as f:
    db_username = f.readline().strip()
    db_password = f.readline().strip()


class DBOperationalSuccess:
    def __init__(self, fetched=None):
        if fetched is None:
            fetched = [(0,)]
        self.fetched_info = fetched


class BotOperationalSuccess:
    def __init__(self, msg=""):
        self.message = msg


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
            except (DuplicateTable, DuplicateDatabase):  # Only for create_db/table
                return DBOperationalSuccess()
            try:
                return DBOperationalSuccess(cursor.fetchall())
            except psycopg2.ProgrammingError:  # Nothing to fetch
                return DBOperationalSuccess()
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
    return open_connection(query="INSERT INTO list_of_all_users (username) VALUES ('{0}');".format(table_name))


def init_new_user(message):  # check existence of user and create table if necessary
    query = """SELECT COUNT(1) 
                FROM list_of_all_users 
                WHERE username = '{0}';
            """.format(message.lower())  # TODO: it seems postgres does not recognize capital letters
    if open_connection(query=query).fetched_info[0][0] != 0:  # (0, ) - no record found in list_of_all_users
        return BotOperationalSuccess("Table already exists!")
    else:
        try:
            create_table(message)
            return BotOperationalSuccess("Table successfully created!")
        except psycopg2.Error as Error:
            raise Error


def lookup(username, col, user_date, order="amount"):
    query = "SELECT amount, type, user_time, comment FROM {0} WHERE {1}='{2}' ORDER BY {3}".format(username, col,
                                                                                                   user_date, order)
    return open_connection(query=query)


def lookup_month(username, col, user_date, order="day"):
    query = "SELECT amount, type, day, user_time, comment FROM {0} WHERE {1}='{2}' ORDER BY {3}".format(username, col,
                                                                                                        user_date,
                                                                                                        order)
    return open_connection(query=query)


def user_help_categories(username):
    query = "SELECT type FROM {0}".format(username)
    return open_connection(query=query)


def add(username, amount, t_type, day, time, comment):
    query = "INSERT INTO {0} (amount, type, day, creation_time, user_time, comment)" \
            " VALUES ({1}, '{2}', '{3}', CURRENT_TIMESTAMP, '{4}', '{5}');".format(username, amount,
                                                                                   t_type,
                                                                                   day,
                                                                                   time,
                                                                                   comment)
    return open_connection(query=query)
