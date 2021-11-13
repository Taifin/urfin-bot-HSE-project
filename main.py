import telebot

with open('token.txt') as f:
    token = f.readline().strip()
bot = telebot.TeleBot(token)


@bot.message_handler(content_types=['text'])
def get_message(message):
    if message.text in ['Hi', 'Hello', 'Privet', 'Привет']:
        bot.send_message(message.from_user.id, "Ну привет-привет")
    else:
        bot.send_message(message.from_user.id, "Пока, получается")


bot.polling(none_stop=True, interval=0)
