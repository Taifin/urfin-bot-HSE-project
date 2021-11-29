# urfin - a telegram personal finances' bot created as a Python project at HSE

### Description:

Urfin - is a telegram bot that allows you to log your spending in an (almost) convenient way and access them in different ways.
It is created using a [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) wrapper for TelegramAPI and 
PostgreSQL database to store users' info.

### Using bot:

1. Launch `bot.py` source file. 
3. Search for "@ur_fin_bot" in telegram and type `/start`.

### Supported commands:
`/start` - initialize a table in bot's database to store all your data.

`/help` - show all supported commands with short descriptions

`/add` - add new transaction record into database

`/addhelp` - it might be helpful to check the format of `/add` command

`/add_inline` - more simple and quick way to add new record [WORK IN PROGRESS]

`/daylookup` - get information on all the records from specified day

`/categorylookup` - get information on all the records from specified category

`/monthlookup` - bot will create a .xlsx table with all your records from specified month

### Coming soon:

* New (and more readable) output format of `/...lookup` commands.
* Syntax changes for some commands.
* Inline keyboard and general interface improvements.
* Sorting of data from `/...lookup` commands (and better interaction with database in general).
* Better format of month-lookup table.
* Cloud deployment (heroku).
* Source code improvements, because it's rubbish.
* Personal log-files with errors.

### Packages and requirements:

* `python-telegram-bot` 13.8.1 - TelegramBotAPI
* `psycopg2` 2.9.2 - PostgresSQL interaction
* `openpyxl` 3.0.9 - .xlsx tables support
* `postgresql` 14.1  - PostgreSQL

# Warning:

Please, be careful using the bot - it is in an early development stage. 
Main functional must work if you will be following input format. It's unlikely you'll break something,
but there may occur **unexpected effects**.

Also remember that bot is using default username 
and password for PostgreSQL that is installed on your system ("postgres" and "postgres"). You can change it manually in file 'config/database.txt'.

Also, the source code, as 'Coming soon' section states, is a complete rubbish, because I was
mostly focusing on making certain features for at least somehow, not on making them good-looking. I hope
you won't want to gouge out your eyes (because sometimes I do :') ).
