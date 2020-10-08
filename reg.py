import telebot
import json

TOKEN = "1349220158:AAH-7hJbNeleiAQmTbWKQKpcL17cKPrG2Wc"

bot = telebot.TeleBot(TOKEN)
group = {}
adminpass = "padla"

print("[LOG] Started ")

@bot.message_handler(commands=['clear'])
def adminauth(message):
    print(f"[LOG] @{message.chat.username} REQUESTING ADMIN CONTROL")
    bot.send_message(message.chat.id, 'Для выполнения данной команды необходим доступ. Введите пароль: ')
    bot.register_next_step_handler(message, clear)

def clear(message):
    if(str(message.text) != adminpass):
        bot.send_message(message.chat.id, 'Неверный пароль. В доступе отказано')
        print(f"[LOG] @{message.chat.username} INVALID AUTH CODE -> {message.text}")
        return
    bot.send_message(message.chat.id, 'Введите номер группы: ')
    print(f"[LOG] @{message.chat.username} AUTH SUCCESS")
    bot.register_next_step_handler(message, clearquery)

def clearquery(message):
    with open('query.json', 'r') as f:
        data = json.load(f)
    data[str(message.chat.id)] = None
    with open('query.json', 'w') as f:
        json.dump(data, f, indent=4)
    bot.send_message(message.chat.id, f'Очередь группы {message.text} успешно очищена')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в систему регистрации! /help для более подробной информации")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "/reg - Начать процесс регистрации и добавления в очередь\n/query - Текущая очередь")

@bot.message_handler(commands=['query'])
def getnumber(message):
    global group
    bot.send_message(message.chat.id, "Введите номер группы: ")
    print(f"[LOG] @{message.chat.username} requested query")
    bot.register_next_step_handler(message, getquery);
def getquery(message):
    print(f"[LOG] @{message.chat.username} -> {message.text}")
    with open('query.json', 'r') as f:
        data = json.load(f)
    if(str(message.text) not in data):
        print(f"[LOG] @{message.chat.username} LIST ERROR")
        bot.send_message(message.chat.id, f"Для группы {message.text} не найден список регистрации")
        return
    output = "Размер очереди: "
    for i in data[str(message.text)]:
        output += data[str(message.text)][i] + '\n'
    bot.send_message(message.chat.id, output)
    print(f"[LOG] @{message.chat.username} <- \n {output}")

@bot.message_handler(commands=['reg'])
def registration(message):
    print(f"[LOG] @{message.chat.username} started registration")
    bot.send_message(message.chat.id, "Начинаем регистрацию. Введите ваш номер группы: ")
    bot.register_next_step_handler(message, groupinput)

def groupinput(message):
    global group
    uinfo = f"{message.from_user.first_name} {message.from_user.last_name} : @{message.chat.username}"
    with open('query.json', 'r') as f:
        data = json.load(f)
    for i in data[str(message.text)]:
        if str(i) == uinfo:
            bot.send_message(message.chat.id, "Вы уже зарегестрированны!")
            return
    if(message.text not in data):
        data[str(message.text)] = {}
    group[message.chat.id] = str(message.text)
    print(f"[LOG] @{message.chat.username} -> {message.text} {uinfo}")
    data[message.text][str(int(data[message.text]['count']) + 1)] = uinfo
    data[message.text]['count'] = str(int(data[message.text]['count']) + 1)
    with open('query.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f"[LOG] @{message.chat.username} -> {message.text}. Finished registration")
    bot.send_message(message.chat.id, 'Регистрация завершена! Ваш порядковый номер в очереди: ' + str(data[group[message.chat.id]]['count']))


def nameinput(message):
    with open('query.json', 'r') as f:
        data = json.load(f)
    if('count' not in data[group[message.chat.id]]):
        data[group[message.chat.id]]['count'] = '0'
    data[group[message.chat.id]][str(int(data[group[message.chat.id]]['count']) + 1)] = message.text
    data[group[message.chat.id]]['count'] = str(int(data[group[message.chat.id]]['count']) + 1)
    with open('query.json', 'w') as f:
            json.dump(data, f, indent=4)
    print(f"[LOG] @{message.chat.username} -> {message.text}. Finished registration")
    bot.send_message(message.chat.id, 'Регистрация завершена! Ваш порядковый номер в очереди: ' + str(data[group[message.chat.id]]['count']))
bot.polling()
