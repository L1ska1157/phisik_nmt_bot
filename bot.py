import telebot
from telebot import types
import json
from User import User



print('Running...')

API_TOKEN = '7212098902:AAEfcC8FQJVQ6nWouBI3H63eNlft1nFhJFk'

bot = telebot.TeleBot(API_TOKEN)

# => buttons for main keyboard
btn_get_task = types.KeyboardButton('Отримати задачу')
btn_redo = types.KeyboardButton('Повторення')
btn_add = types.KeyboardButton('Додати теми')
btn_show_progress = types.KeyboardButton('Переглянути прогрес')
btn_delete_progress = types.KeyboardButton('Скинути прогрес')

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(btn_get_task, btn_redo, btn_add, btn_show_progress,
              btn_delete_progress)

btn_back = types.InlineKeyboardButton('Назад', callback_data='back')


# => function to load object data from json
def obj_creation(dict):
    return User(**dict)


# => loading users list
try:
    with open('users_data/users.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        user = {k: obj_creation(v) for k, v in json_data.items()}
except Exception as ex:
    print(str(ex))
    user = {}
# => information check
print(user)


# => start function. saying hello, saving new users in users dictionary and then in json file
@bot.message_handler(commands=['start'])
def start(message):
    global user
    global main_menu
    print('start')

    # => creating new user profile
    user[str(message.chat.id)] = User(message.chat.id)

    for k, v in user.items():
        print(type(k))

    # => saving new user
    with open('users_data/users.json', 'w', encoding='utf-8') as f:
        json_data = {str(k): v.to_dict() for k, v in user.items()}
        json.dump(json_data, f, indent=4)

    bot.send_message(
        message.chat.id,
        'Привіт! Я допоможу тобі підготуватися до НМТ з фізики. Для детального ознайомлення з кожною функцією: /help',
        reply_markup=main_menu)


# => instruction for using. explaining what every function is doing and what limits they have
@bot.message_handler(commands=['help'])
def help(message):
    print('help')

    with open('help.txt', 'r', encoding='utf-8') as f:
        help = f.read()

    bot.send_message(message.chat.id, help)


# => giving random UNDONE task from tasks list(individual for every user)
@bot.message_handler(commands=['get_task'])
def get_task(message):
    global user
    global btn_back
    global main_menu
    print('get_task')

    btn_anouther_task = types.InlineKeyboardButton(
        'Змінити задачу', callback_data='anouther_task')

    markup = types.InlineKeyboardMarkup()
    markup.add(btn_back, btn_anouther_task)

    try:
        is_text, title, mes = user[str(message.chat.id)].get_task(False)

        # => message sending command depends of question format: image or text
        bot.send_message(message.chat.id,
                         title,
                         reply_markup=types.ReplyKeyboardRemove())
        if is_text:
            bot.send_message(message.chat.id, mes, reply_markup=markup)
        else:
            bot.send_photo(message.chat.id, mes, reply_markup=markup)
        
        global mes_id    
        
        mes_id = message.message_id + 2
        
    except:
        mes = user[str(message.chat.id)].get_task(False)
        bot.send_message(message.chat.id, mes, reply_markup=main_menu)


# => showing progress for all tasks end for each theme in format:
#    General progress:           n%
#    theme 1                     n%
#    theme 2                     n%
@bot.message_handler(commands=['show_progress'])
def show_progress(message):
    global user
    print('show progress')

    bot.send_message(message.chat.id, user[str(message.chat.id)].show_progress())



# => adding new themes to themes list, so tasks from this themes also would be included
@bot.message_handler(commands=['add_theme'])
def add_theme(message):
    global user
    global btn_back

    markup = types.InlineKeyboardMarkup()
    markup.add(btn_back)

    bot.send_message(message.chat.id,
                     'Напишіть номери тем, які ви вже вивчили:',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, '1. Механіка\n' \
    '2. Молекулярна фізика і термодинаміка\n'\
    '3. Електродинаміка\n'\
    '4. Коливання та хвилі. Оптика\n'\
    '5. Квантова фізика. Елементи теорії відносності\n' \
    '(наприклад "1 2 3 4 5")', reply_markup=markup)# => after this, proccesing ends in general message proc. function

    user[str(message.chat.id)].is_add = True



# => deleting all user progress(reask to make shure)
@bot.message_handler(commands=['delete_progress'])
def delete_progress(message):
    print('delete progress')

    btn_no = types.InlineKeyboardButton('Ні', callback_data='back')
    btn_yes = types.InlineKeyboardButton('Так', callback_data='delete_data')

    markup = types.InlineKeyboardMarkup()
    markup.add(btn_no, btn_yes)

    bot.send_message(message.chat.id,
                     'Всі ваші правильні відповіді буде видалено',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id,
                     'Ви впевнені, що хочете видалити свій прогрес?',
                     reply_markup=markup)


# => the same as get_task, but ignoring task complited status
@bot.message_handler(commands=['redo_all_tasks'])
def redo(message):
    global user
    global btn_back
    print('redo')

    btn_anouther_task = types.InlineKeyboardButton(
        'Змінити задачу', callback_data='anouther_task')

    markup = types.InlineKeyboardMarkup()
    markup.add(btn_back, btn_anouther_task)

    is_text, title, mes = user[str(message.chat.id)].get_task(True)

    # => message sending command depends of question format: image or text
    bot.send_message(message.chat.id,
                     title,
                     reply_markup=types.ReplyKeyboardRemove())
    if is_text:
        bot.send_message(message.chat.id, mes, reply_markup=markup)
    else:
        bot.send_photo(message.chat.id, mes, reply_markup=markup)


# => proccesing all other text messages (answears cheaking, themes adding)
@bot.message_handler(content_types=['text'])
def mes_proc(message):
    global user
    global main_menu
    global mes_id

    # => end of themes adding function
    if user[str(message.chat.id)].is_add:
        print('add theme')
        t_list = message.text.split()
        user[str(message.chat.id)].add_theme(t_list)
        bot.edit_message_reply_markup(message.chat.id,
                                      message.message_id - 1,
                                      reply_markup=None)
        bot.send_message(message.chat.id, 'Є', reply_markup=main_menu)

    # => cheking answers after giving task
    if user[str(message.chat.id)].current_q:
        print('check answears')
        
        mes = user[str(message.chat.id)].check_ans(
            message.text.strip().replace(',', '.'))
        
        bot.send_message(message.chat.id, mes)
        
        if mes == '✅':
            # => going back to main menu
            user[str(message.chat.id)].back()
            
            # => deleting inline keyboard from task message
            bot.edit_message_reply_markup(message.chat.id,
                                      mes_id,
                                      reply_markup=None)
            
            # => adding replay keyboard
            bot.send_message(message.chat.id,
                         'Повертаюся...',
                         reply_markup=main_menu)

    # => activating right functions after choosing any option on keyboard
    if message.text.strip().lower() == 'отримати задачу':
        get_task(message)

    if message.text.strip().lower() == 'повторення':
        redo(message)

    if message.text.strip().lower() == 'додати теми':
        add_theme(message)

    if message.text.strip().lower() == 'переглянути прогрес':
        show_progress(message)

    if message.text.strip().lower() == 'скинути прогрес':
        delete_progress(message)


# => proccesing callback data
@bot.callback_query_handler(func=lambda call: True)
def callback_proc(call):
    global user
    global btn_back
    global main_menu

    if call.data == 'anouther_task':
        # => getting new task
        is_text, title, mes = user[str(call.message.chat.id)].get_task(False)

        # => creating keyboard markup
        btn_anouther_task = types.InlineKeyboardButton(
            'Змінити задачу', callback_data='anouther_task')
        markup = types.InlineKeyboardMarkup()
        markup.add(btn_back, btn_anouther_task)

        # => deleting keyboard from previous message
        bot.edit_message_reply_markup(call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=None)

        # => sending new task
        bot.send_message(call.message.chat.id, title)
        if is_text:
            bot.send_message(call.message.chat.id, mes, reply_markup=markup)
        else:
            bot.send_photo(call.message.chat.id, mes, reply_markup=markup)

    if call.data == 'back':
        # => saving that bot is not waiting for answer or theme adding
        user[str(call.message.chat.id)].back()
        # => deleting inline keyboard from task message
        bot.edit_message_reply_markup(call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=None)
        # => adding replay keyboard
        bot.send_message(call.message.chat.id,
                         'Повертаюся...',
                         reply_markup=main_menu)

    if call.data == 'delete_data':
        user[str(call.message.chat.id)].delete_progress()
        bot.edit_message_reply_markup(call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=None)
        bot.send_message(call.message.chat.id,
                         'Прогрес скинуто',
                         reply_markup=main_menu)


bot.infinity_polling()