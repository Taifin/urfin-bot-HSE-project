import psycopg2

try:
    connection = psycopg2.connect(user="postgres", password='taifin', host='localhost', port='5432')
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    print("Информация о сервере PostgreSQL")
    print(connection.get_dsn_parameters(), "\n")
    # Выполнение SQL-запроса
    cursor.execute("SELECT version();")
    # Получить результат
    record = cursor.fetchone()
    print("Вы подключены к - ", record, "\n")
except (Exception, psycopg2.Error) as Error:
    print('Ошибка при подключении:', Error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print('Соединение закрыто')
