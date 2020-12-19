import os
import telebot


# BOT PROPERTIES
admins = ['604005377']

with open('tg_token.txt', 'r') as token:
    tg_token = token.readline()
# token = ''

# COMMAND REPLIES
add_text = 'Привет, ты будешь добавлен в список людей, которым будет рассылаться нахождение ночного (пока что работает только для второго этажа)'
remove_text = 'Тебе больше не будут приходить сообщения\nПока!'
not_admin_text = 'Ты не являешься админом и не можешь отправлять сообщения для всех участников'
help_text = """
            Доступные команды:
            /start - добавляет пользователя в список рассылки
            /remove - убирает пользователя из списка рассылки
            /help - команды бота
            /about - информация о боте
            """
about_text = 'Бот создан для оповещения фымышат об какой-то активности на их этаже в ночное время суток (в основном это означает, что это ночной)'


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def add_id(message):
    bot.send_message(message.chat.id, add_text)
    bot.send_message(message.chat.id, help_text)
    
    if 'database.txt' not in os.listdir('.'):
        f = open('database.txt', 'w')
        f.close()
    
    ids = []
    with open('database.txt', 'r') as read_data:
        ids = [i.replace('\n', '') for i in read_data]
    
    if str(message.chat.id) not in ids:
        with open('database.txt', 'a') as data:
            data.write('{}\n'.format(message.chat.id))


@bot.message_handler(commands=['remove'])
def remove_id(message):
    ids = []
    
    with open('database.txt', 'r') as data:
        ids = data.readlines()
    
    if str(message.chat.id) + '\n' in ids:
        del ids[ids.index(str(message.chat.id) + '\n')]
    
    with open('database.txt', 'w') as write_data:
        write_data.writelines(ids)
    
    bot.send_message(message.chat.id, remove_text)


@bot.message_handler(commands=['help'])
def get_help(message):
    bot.send_message(message.chat.id, help_text)
    

@bot.message_handler(commands=['about'])
def get_about(message):
    bot.send_message(message.chat.id, about_text)


@bot.message_handler(commands=['send'])
def send_text(message):
    if str(message.chat.id) not in admins:
        bot.send_message(message.chat.id, not_admin_text)
        return
    
    with open('database.txt', 'r') as data:
        ids = data.readlines()
    
    for i in ids:
        bot.send_message(i, 'Ночной!!!')


bot.polling()