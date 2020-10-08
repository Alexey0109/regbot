import telebot
import json
import configparser
import datetime
from datetime import datetime as t

print(f'[LOG] {str(t.now())} | Started')
print(f'[LOG] {str(t.now())} | STATUS: STARTING')
print(f'[LOG] {str(t.now())} | LOADING: LOADING CONFIG')

config = configparser.ConfigParser()
config.read("mainconfig.cfg")
print(f'[LOG] {str(t.now())} | LOADING: LOADED CONGIF FILE')
TOKEN = config['BOT']['TOKEN']
print(f'[LOG] {str(t.now())} | LOADING: CURRENT TOKEN: {TOKEN}')
bot = telebot.TeleBot(TOKEN)
adminpass = config['BOT']['ADMINPASS']

print(f'[LOG] {str(t.now())} | LOADING: ADMINPASS: {adminpass}')

@bot.message_handler(commands=['new', 'add', 'create', 'open', 'regopen', 'overwrite', 'clear', 'remove', 'delete', 'clean', 'cleanup'])
def new(message):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} REQUESTING ADMIN ACCESS')
    bot.send_message(message.chat.id, config['TXTINTERFACE']['PASSWARN'])
    bot.register_next_step_handler(message, passw)

def passw(message):
    if(message.text != adminpass):
        print(f'[LOG] {str(t.now())} | @{message.from_user.username} INCORRECT PASS GIVEN')
        bot.send_message(message.chat.id, config['TXTINTERFACE']['PASS_ERR'])
        return
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} ACCESS GRANTED')
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'])
    bot.register_next_step_handler(message, addgroupinput)

def addgroupinput(message):
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None:
        data[str(message.text)] = {}
    output = str()
    for i in data[str(message.text)]:
        output += i + " | "
    bot.send_message(message.chat.id, f"Введите предмет:")
    bot.register_next_step_handler(message, addlab, message.text)

def addlab(message, group):
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(group) not in data or data[group] == None:
        data[str(group)] = {}
    data[str(group)][message.text] = {}
    bot.send_message(message.chat.id, f"Новая очередь регистрации на предмет {message.text} открыта")
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} Created new queue: {message.text}')
    with open('query.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['start'])
def start(message):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} started')
    bot.send_message(message.chat.id, "Добро пожаловать в систему регистрации! /help для более подробной информации")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "/reg - Начать процесс регистрации и добавления в очередь\n/query - Текущая очередь")

@bot.message_handler(commands=['query', 'list', 'registered', 'queue', 'getlist'])
def getnumber(message):
    global group
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'])
    print(f"[LOG] {str(t.now())} | @{message.chat.username} requested query")
    bot.register_next_step_handler(message, getlab);

def getlab(message):
    with open('query.json', 'r') as f:
        data = json.load(f)
    if message.text not in data or data[message.text] == None:
        bot.send_message(message.chat.id, f"Для группы {message.text} не найден список регистрации")
        return
    if str(message.text) not in data or data[str(message.text)] == None:
        data[str(message.text)] = {}
    output = str()
    for i in data[str(message.text)]:
        output += i + " | "
    bot.send_message(message.chat.id, f"Введите предмет: {output}")
    bot.register_next_step_handler(message, getquery, message.text);

def getquery(message, group):
    print(f'[LOG] {str(t.now())} | @{message.chat.username} -> {message.text}')
    with open('query.json', 'r') as f:
        data = json.load(f)
    if data[group] == None:
        bot.send_message(message.chat.id, f"Для группы {group}:{message.text} не найден список регистрации")
        return
    if(group not in data or str(message.text) not in data[group] or 'query' not in data[group][str(message.text)]):
        print(f'[LOG] {str(t.now())} | @{message.chat.username} -> {message.text} LIST ERROR')
        bot.send_message(message.chat.id, f"Для группы {group}:{message.text} не найден список регистрации")
        return
    output = str()
    counter = 0
    for i in data[group][str(message.text)]['query'].values():
        counter += 1
        output += f"{str(counter)}: {i['fname']} {i['lname']} : @{i['uname']}\n"
    bot.send_message(message.chat.id, output)
    print(f"[LOG] {str(t.now())} | @{message.chat.username} <- \n {output}")

@bot.message_handler(commands=['reg', 'register', 'addme', 'reglist'])
def registration(message):
    print(f"[LOG] {str(t.now())} | @{message.chat.username} started registration")
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'])
    bot.register_next_step_handler(message, groupinput)

def groupinput(message):
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None:
        data[str(message.text)] = {}
    output = str()
    for i in data[str(message.text)]:
        output += i + " | "
    bot.send_message(message.chat.id, f"Введите предмет: {output}")
    bot.register_next_step_handler(message, register, message.text)

def register(message, group):
    uinfo = {}
    uinfo['id'] = str(message.chat.id)
    uinfo['fname'] = str(message.from_user.first_name)
    uinfo['lname'] = str(message.from_user.last_name)
    uinfo['uname'] = str(message.chat.username)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(group) not in data or data[group] == None:
        data[str(group)] = {}
    if(message.text not in data[str(group)]):
        bot.send_message(message.chat.id, "Регистрация на этот предмет еще не начата или неверно указано название предмета") 
        return
    if('count' not in data[str(group)][message.text]):
        data[str(group)][message.text]['count'] = '0'
    if('query' not in data[str(group)][message.text]):
        data[str(group)][message.text]['query'] = {}
    for i in data[str(group)][message.text]['query'].values():
        if(i['id'] == str(message.chat.id)):
            bot.send_message(message.chat.id, config['TXTINTERFACE']['REGERROR'])
            return
    print(f"[LOG] {str(t.now())} | @{message.chat.username} -> {group} {uinfo}")
    data[group][message.text]['query'][str(int(data[group][message.text]['count']) + 1)] = uinfo
    data[group][message.text]['count'] = str(int(data[group][message.text]['count']) + 1)
    with open('query.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f"[LOG] {str(t.now())} | @{message.chat.username} -> {group}. Finished registration")
    bot.send_message(message.chat.id, 'Регистрация завершена! Ваш порядковый номер в очереди: ' + str(data[str(group)][message.text]['count']))
bot.polling()
