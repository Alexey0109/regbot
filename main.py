import telebot
import json
import configparser
import datetime
import schedule
import threading
import time
from datetime import datetime as t
from telebot import types

print(f'[LOG] {str(t.now())} | Started')
print(f'[LOG] {str(t.now())} | STATUS: STARTING')
print(f'[LOG] {str(t.now())} | LOADING: LOADING CONFIG')

config = configparser.ConfigParser()
config.read("mainconfig.cfg")
print(f'[LOG] {str(t.now())} | LOADING: LOADED CONGIF FILE')

TOKEN = config['BOT']['TOKEN']
CRASHREPORT = config['BOT']['CRASHREPORT']
adminpass = config['BOT']['ADMINPASS']

print(f'[LOG] {str(t.now())} | LOADING: CURRENT TOKEN: {TOKEN}')

bot = telebot.TeleBot(TOKEN)
crashreport = telebot.TeleBot(TOKEN)

print(f'[LOG] {str(t.now())} | LOADING: ADMINPASS: {adminpass}')

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == "addsubj":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Следуйте пунктам:")
            create_new_query(call.message)
        if call.data == "remsubj":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Следуйте пунктам:")
            delete_query(call.message)

@bot.message_handler(commands=['stop'])
def stop_schedule(message):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} REQUESTING ADMIN ACCESS')
    bot.send_message(message.chat.id, config['TXTINTERFACE']['PASSWARN'])
    bot.register_next_step_handler(message, stop_schedule_password_input)

def stop_schedule_password_input(message):
    if(message.text != adminpass):
        print(f'[LOG] {str(t.now())} | @{message.from_user.username} INCORRECT PASS GIVEN')
        bot.send_message(message.chat.id, config['TXTINTERFACE']['PASS_ERR'])
        return
    with open('query.json', 'r') as f:
        data = json.load(f)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in data:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'], reply_markup=keyboard)
    bot.register_next_step_handler(message, stop_schedule_group_input)

def stop_schedule_group_input(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None:
        data[str(message.text)] = {}
    for i in data[message.text]:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, f"Введите предмет", reply_markup=keyboard)
    bot.register_next_step_handler(message, stop_schedule_remove, message.text)

def stop_schedule_remove(message, group):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} Deleted scheduled task: {group} {message.text}')
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f'Отменено расписание для группы {group}:{message.text}', reply_markup=keyboard)
    schedule.clear(tag=f'{group}:{message.text}')

@bot.message_handler(commands=['schedule'])
def schedule_task(message):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} REQUESTING ADMIN ACCESS')
    bot.send_message(message.chat.id, config['TXTINTERFACE']['PASSWARN'])
    bot.register_next_step_handler(message, schedule_password_input)

def schedule_password_input(message):
    if(message.text != adminpass):
        print(f'[LOG] {str(t.now())} | @{message.from_user.username} INCORRECT PASS GIVEN')
        bot.send_message(message.chat.id, config['TXTINTERFACE']['PASS_ERR'])
        return
    with open('query.json', 'r') as f:
        data = json.load(f)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in data:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'], reply_markup=keyboard)
    bot.register_next_step_handler(message, schedule_group_input)

def schedule_group_input(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None:
        data[str(message.text)] = {}
    for i in data[message.text]:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, f"Введите предмет", reply_markup=keyboard)
    bot.register_next_step_handler(message, schedule_day_input, message.text)

def schedule_day_input(message, group):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button = types.KeyboardButton(text='Понедельник')
    keyboard.add(button)
    button = types.KeyboardButton(text='Вторник')
    keyboard.add(button)
    button = types.KeyboardButton(text='Среда')
    keyboard.add(button)
    button = types.KeyboardButton(text='Четверг')
    keyboard.add(button)
    button = types.KeyboardButton(text='Пятница')
    keyboard.add(button)
    button = types.KeyboardButton(text='Суббота')
    keyboard.add(button)
    button = types.KeyboardButton(text='Воскресенье')
    keyboard.add(button)
    bot.send_message(message.chat.id, 'Введите день: ', reply_markup=keyboard)
    bot.register_next_step_handler(message, schedule_time_input, group, message.text)

def schedule_time_input(message, group, subject):
    keyboard = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Введите время в формате (24h) XX:XX\n(Например 20:00) ', reply_markup=keyboard)
    bot.register_next_step_handler(message, schedule_add_scheduler, group, subject, message.text)

def schedule_add_scheduler(message, group, subject, day):
    keyboard = types.ReplyKeyboardRemove()
    if(day == 'Понедельник'):
        schedule.every().monday.at(message.text).do(schedule_add, message, subject, f"{group}:{subject}").tag(group)
    elif(day == 'Вторник'):
        schedule.every().tuesday.at(message.text).do(schedule_add, message, subject, f"{group}:{subject}").tag(group)
    elif(day == 'Среда'):
        schedule.every().wednesday.at(message.text).do(schedule_add, message, subject, f"{group}:{subject}").tag(group)
    elif(day == 'Черверг'):
        schedule.every().thursday.at(message.text).do(schedule_add, message, subject, f"{group}:{subject}").tag(group)
    elif(day == 'Пятница'):
        schedule.every().friday.at(message.text).do(schedule_add, message, subject, f"{group}:{subject}").tag(group)
    elif(day == 'Суббота'):
        schedule.every().saturday.at(message.text).do(schedule_add, message, subject, f"{group}:{subject}").tag(group)
    elif(day == 'Воскресенье'):
        schedule.every().sunday.at(message.text).do(schedule_add, message, subject, f"{group}:{subject}").tag(group)
    else:
        bot.send_message(message.chat.id, 'Расписание не запущено: неверные входные данные', reply_markup=keyboard)
        return
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} Created new schedule: {day} {message.text} : {group} {subject}')
    bot.send_message(message.chat.id, 'Запущено расписание!', reply_markup=keyboard)
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()

def schedule_add(message, subject, group):
    schedule_thread = threading.Thread(target=schedule_add_thread, args=(message, group, subject, ))
    schedule_thread.start()

def schedule_add_thread(message, group, subject):
    keyboard = types.ReplyKeyboardRemove()
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(group) not in data or data[group] == None:
        data[str(group)] = {}
    data[str(group)][subject] = {}
    bot.send_message(message.chat.id, f"Новая очередь регистрации на предмет {subject} открыта", reply_markup=keyboard)
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} Created new queue: {subject}')
    with open('query.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['adminmenu', 'admin'])
def admin(message):
    keyboard = types.InlineKeyboardMarkup()
    add_button = types.InlineKeyboardButton(text="Добавить предмет", callback_data='addsubj')
    keyboard.add(add_button)
    remove_button = types.InlineKeyboardButton(text="Удалить предмет", callback_data='remsubj')
    keyboard.add(add_button)
    bot.send_message(message.chat.id, 'Выберите пункт:', reply_markup=keyboard)

@bot.message_handler(commands=['new', 'add', 'create', 'open', 'regopen', 'overwrite'])
def create_new_query(message):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} REQUESTING ADMIN ACCESS')
    bot.send_message(message.chat.id, config['TXTINTERFACE']['PASSWARN'])
    bot.register_next_step_handler(message, create_new_query_password_input)

def create_new_query_password_input(message):
    if(message.text != adminpass):
        print(f'[LOG] {str(t.now())} | @{message.from_user.username} INCORRECT PASS GIVEN')
        bot.send_message(message.chat.id, config['TXTINTERFACE']['PASS_ERR'])
        return
    with open('query.json', 'r') as f:
        data = json.load(f)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in data:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'], reply_markup=keyboard)
    bot.register_next_step_handler(message, create_new_query_group_input)

def create_new_query_group_input(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None:
        data[str(message.text)] = {}
    for i in data[message.text]:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, f"Введите предмет", reply_markup=keyboard)
    bot.register_next_step_handler(message, create_new_query_add, message.text)

def create_new_query_add(message, group):
    keyboard = types.ReplyKeyboardRemove()
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(group) not in data or data[group] == None:
        data[str(group)] = {}
    data[str(group)][message.text] = {}
    bot.send_message(message.chat.id, f"Новая очередь регистрации на предмет {message.text} открыта", reply_markup=keyboard)
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} Created new queue: {message.text}')
    with open('query.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['deletequery', 'delq'])
def delete_query(message):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} REQUESTING ADMIN ACCESS')
    bot.send_message(message.chat.id, config['TXTINTERFACE']['PASSWARN'])
    bot.register_next_step_handler(message, delete_query_password_input)

def delete_query_password_input(message):
    if(message.text != adminpass):
        print(f'[LOG] {str(t.now())} | @{message.from_user.username} INCORRECT PASS GIVEN')
        bot.send_message(message.chat.id, config['TXTINTERFACE']['PASS_ERR'])
        return
    print(f"[LOG] {str(t.now())} | @{message.chat.username} started registration")
    with open('query.json', 'r') as f:
        data = json.load(f)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in data:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'], reply_markup=keyboard)
    bot.register_next_step_handler(message, delete_query_group_input)

def delete_query_group_input(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None:
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f'Для группы {message.text} не найдена открытая очередь регистрации', reply_markup=keyboard)
        return 
    for i in data[message.text]:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, f"Введите предмет", reply_markup=keyboard)
    bot.register_next_step_handler(message, delete_query_del, message.text)

def delete_query_del(message, group):
    keyboard = types.ReplyKeyboardRemove();
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(group) not in data or data[group] == None:
        data[str(group)] = {}
    if str(message.text) not in data[group]:
        data[str(group)][message.text] = {}
    del data[str(group)][message.text]
    bot.send_message(message.chat.id, f"Очередь регистрации на предмет {message.text} закрыта", reply_markup=keyboard)
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} Deleted queue: {message.text}')
    with open('query.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['start'])
def start(message):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} started')
    bot.send_message(message.chat.id, "Добро пожаловать в систему регистрации! /help для более подробной информации")

@bot.message_handler(commands=['help'])
def help(message):
    print(f'[LOG] {str(t.now())} | @{message.from_user.username} help file requested')
    bot.send_message(message.chat.id, "/reg - Начать процесс регистрации и добавления в очередь\n/query - Текущая очередь")

@bot.message_handler(commands=['query', 'list', 'registered', 'queue', 'getlist'])
def get_group_number(message):
    with open('query.json', 'r') as f:
        data = json.load(f)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in data:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'], reply_markup=keyboard)
    print(f"[LOG] {str(t.now())} | @{message.chat.username} requested query")
    bot.register_next_step_handler(message, get_query_name);

def get_query_name(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None:
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f'Для группы {message.text} не найдена открытая очередь регистрации', reply_markup=keyboard)
        return 
    for i in data[message.text]:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, f"Введите предмет", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_query, message.text)

def get_query(message, group):
    keyboard = types.ReplyKeyboardRemove()
    print(f'[LOG] {str(t.now())} | @{message.chat.username} -> {message.text}')
    with open('query.json', 'r') as f:
        data = json.load(f)
    if data[group] == None:
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f"Для группы {group}:{message.text} не найден список регистрации", reply_markup=keyboard)
        return
    if(group not in data or str(message.text) not in data[group] or 'query' not in data[group][str(message.text)]):
        keyboard = types.ReplyKeyboardRemove()
        print(f'[LOG] {str(t.now())} | @{message.chat.username} -> {message.text} LIST ERROR')
        bot.send_message(message.chat.id, f"Для группы {group}:{message.text} не найден список регистрации", reply_markup=keyboard)
        return
    output = str(f'Список регистрации на {message.text}:\n')
    counter = 0
    for i in data[group][str(message.text)]['query'].values():
        counter += 1
        output += f"{str(counter)}: {i['fname']} {i['lname']} : @{i['uname']}\n"
    bot.send_message(message.chat.id, output, reply_markup=keyboard)
    print(f"[LOG] {str(t.now())} | @{message.chat.username} <- \n{output}")

@bot.message_handler(commands=['reg', 'register', 'addme', 'reglist'])
def registration(message):
    print(f"[LOG] {str(t.now())} | @{message.chat.username} started registration")
    with open('query.json', 'r') as f:
        data = json.load(f)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in data:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'], reply_markup=keyboard)
    bot.register_next_step_handler(message, subj_input)

def subj_input(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None:
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f'Для группы {message.text} не найдена открытая очередь регистрации', reply_markup=keyboard)
        return 
    for i in data[message.text]:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, f"Введите предмет", reply_markup=keyboard)
    bot.register_next_step_handler(message, register, message.text)

def register(message, group):
    keyboard = types.ReplyKeyboardRemove()
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
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Регистрация на этот предмет еще не начата или неверно указано название предмета", reply_markup=keyboard) 
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
    bot.send_message(message.chat.id, 'Регистрация завершена! Ваш порядковый номер в очереди: ' + str(data[str(group)][message.text]['count']), reply_markup=keyboard)

@bot.message_handler(commands=['removeme', 'rme'])
def removeme(message):
    print(f"[LOG] {str(t.now())} | @{message.chat.username} wants to exit queue")
    with open('query.json', 'r') as f:
        data = json.load(f)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for i in data:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, config['TXTINTERFACE']['GROUPMSG'], reply_markup=keyboard)
    bot.register_next_step_handler(message, subjr_input)

def subjr_input(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(message.text) not in data or data[str(message.text)] == None or data[str(message.text)] == {}:
        keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f'Для группы {message.text} не найдена открытая очередь регистрации', reply_markup=keyboard)
        return
    for i in data[message.text]:
        button = types.KeyboardButton(text=i)
        keyboard.add(button)
    bot.send_message(message.chat.id, f"Введите предмет", reply_markup=keyboard)
    bot.register_next_step_handler(message, removal, message.text)

def removal(message, group):
    keyboard = types.ReplyKeyboardRemove()
    uinfo = {}
    uinfo['id'] = str(message.chat.id)
    uinfo['fname'] = str(message.from_user.first_name)
    uinfo['lname'] = str(message.from_user.last_name)
    uinfo['uname'] = str(message.chat.username)
    with open('query.json', 'r') as f:
        data = json.load(f)
    if str(group) not in data or data[group] == None:
        bot.send_message(message.chat.id, "Регистрация на этот предмет еще не начата или неверно указано название предмета", reply_markup=keyboard) 
        return
    if(message.text not in data[str(group)]):
        bot.send_message(message.chat.id, "Регистрация на этот предмет еще не начата или неверно указано название предмета", reply_markup=keyboard) 
        return
    if('count' not in data[str(group)][message.text]):
        bot.send_message(message.chat.id, "Регистрация на этот предмет еще не начата или неверно указано название предмета", reply_markup=keyboard) 
        return
    if('query' not in data[str(group)][message.text]):
        bot.send_message(message.chat.id, "Регистрация на этот предмет еще не начата или неверно указано название предмета", reply_markup=keyboard) 
        return
    for i in data[str(group)][message.text]['query']:
        if(data[str(group)][message.text]['query'][i]['id'] == str(message.chat.id)):
            print(i)
            for j in range(int(i) + 1, int(data[str(group)][message.text]['count'])):
                data[str(group)][message.text]['query'][str(j - 1)] = data[str(group)][message.text]['query'][str(j)]
            del data[str(group)][message.text]['query'][data[str(group)][message.text]['count']]
            data[str(group)][message.text]['count'] = str(int(data[str(group)][message.text]['count']) - 1)
            break
    with open('query.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f"[LOG] {str(t.now())} | @{message.chat.username} -> {group}. Finished removal")
    bot.send_message(message.chat.id, 'Вы были исключены из очереди!', reply_markup=keyboard)

bot.polling()
