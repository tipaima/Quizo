import bd
from telebot import *


bot = TeleBot('7562808437:AAGcTtmW11RHYuHYpFp9ytOXbhPi_RRAn0g')


@bot.message_handler(commands=['start'])
def start_message(message):
    if not bd.check_register(message.from_user.id):
        bd.register_user(str(message.from_user.id), message.from_user.first_name, Q=False, q_poz=0)

    bot.send_message(message.from_user.id,
                     'Отлично, давай пройдемся по основным моментам.'
                     'На данный момент тебе доступны команды:'
                     '\n/help - покажет доступные команды и их возможности'
                     '\n/Quiz - переход к квизу'
                     '\n/profile - твой профиль')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id,
                     'Доступные команды:'
                     '\n/help - покажет доступные комманды и их возможности'
                     '\n/Quiz - переход к квизу'
                     '\n/profile - твой профиль')


@bot.message_handler(commands=['profile'])
def info_message(message):
    bot.send_message(message.from_user.id, f'{get_profile(message.from_user.id)}')


@bot.message_handler(commands=['Quiz'])
def Quiz_message(message):
    bd.update('Q', '0', message.from_user.id)
    how_many_quiz = bd.get_all("QUIZ", 'Quiz_id')
    bot.send_message(message.from_user.id, f'На данный момент доступные Quizzes: {len(set(how_many_quiz))}\n'
                                           f'Введите номер квиза, который хотите пройти\n')


@bot.message_handler(func=lambda message: True)
def handle_quiz_number_input(message):
    while bd.get_info("USER", "id", message.from_user.id, "*")[0][2] == '0':
        if message.text in ['/Continue', '/Stop']:
            return quiz_choose(message)

        try:
            number = int(message.text)
            if 0 < number <= len(set(bd.get_all("QUIZ", 'Quiz_id'))):
                Quiz_start(message.text, message.from_user.id)
                bd.update('Q', '1', message.from_user.id)
            else:
                bot.send_message(message.chat.id, 'Quiz под данным номером не существует!')
                bot.send_message(message.chat.id, 'Хотите попробовать еще раз?\n /Continue\n /Stop')
        except ValueError:
            bot.send_message(message.chat.id, 'Вы ввели не число!')
            bot.send_message(message.chat.id, 'Хотите попробовать еще раз?\n /Continue\n /Stop')


def quiz_choose(message):
    if message.text == '/Continue':
        bot.send_message(message.from_user.id, 'Введи номер квиза:')
    elif message.text == '/Stop':
        bot.send_message(message.from_user.id, 'Если захочешь пройти квиз, то используй команду /Quiz')


def Quiz_start(message, id):
    base_info = bd.get_info("QUIZ", "Quiz_id", message, "*")

    if base_info:
        create_poll(base_info, id)
    else:
        bot.send_message(id, 'Квиз не найден!')


def create_poll(base_info, id):
    q_poz = int(bd.get_info("USER", "id", id, "*")[0][3])

    while q_poz < len(base_info):
        quiz_data = base_info[q_poz]
        options = quiz_data[3:7]

        correct_option_id = next((i for i, option in enumerate(options) if option == quiz_data[7]), None)

        bot.send_poll(
            chat_id=id,
            question=quiz_data[2],
            options=options,
            type='quiz',
            correct_option_id=correct_option_id
        )
        q_poz += 1


def get_profile(id):
    profile_info = bd.get_info("USER", "id", id, "*")
    if profile_info:
        name = profile_info[0][1]
        return f"Вот твой профиль:\nИмя: {name}"
    else:
        return "Профиль не найден"


if __name__ == '__main__':
    bd.start_bd()
    try:
        bd.create_bd()
    except:
        print("\033[35m {}".format('DB alredy exists!'))

    bot.polling(skip_pending=True)