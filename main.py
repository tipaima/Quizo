import bd
from telebot import *

bot = TeleBot('TOKEN')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.from_user.id,
                     'Отлично, давай пройдемся по основным моментам.'
                     'На данный момент тебе доступны команды:'
                     '\n/help - покажет доступные команды и их возможности'
                     '\n/Quiz - переход к квизу'
                     '\n/profile - твой профиль'
                     '\n/Change_name - изменить имя')

    if not bd.check_register(message.from_user.id):
        bd.register_user(str(message.from_user.id), message.from_user.first_name, Q=False, q_poz=0)
    else:
        profile_name = bd.get_info("USER", "id", message.from_user.id, "*")[0][1]
        now_name = message.from_user.first_name
        if profile_name != now_name:
            bot.send_message(message.from_user.id,
                             "Ваше имя отличается от того, которое было в последний раз!"
                             "\nЕсли вы хотите его поменять его на актуальное, то используйте команду /Change_name")


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.from_user.id,
                     'Доступные команды:'
                     '\n/help - покажет доступные комманды и их возможности'
                     '\n/Quiz - переход к квизу'
                     '\n/profile - твой профиль'
                     '\n/Change_name - изменить имя')


@bot.message_handler(commands=['profile'])
def info_message(message):
    bot.send_message(message.from_user.id, f'{get_profile(message.from_user.id)}')


@bot.message_handler(commands=['Change_name'])
def info_message(message):
    bot.send_message(message.from_user.id, "Введите новое имя:")
    bd.update('USER', 'Q', '2', message.from_user.id)


@bot.message_handler(commands=['Quiz'])
def Quiz_message(message):
    bd.update('USER', 'Q', '0', message.from_user.id)
    how_many_quiz = bd.get_all("QUIZ", 'Quiz_id')
    bot.send_message(message.from_user.id, f'На данный момент доступные Quizzes: {len(set(how_many_quiz))}\n'
                                           f'Введите номер квиза, который хотите пройти\n')


@bot.message_handler(func=lambda message: True)
def handle_quiz_number_input(message):
    if message.text in ['/Continue', '/Stop']:
        return quiz_choose(message)
    if bd.get_info("USER", "id", message.from_user.id, "*")[0][2] == '2':
        while bd.get_info("USER", "id", message.from_user.id, "*")[0][2] == '2':
            new_name = message.text.strip()
            if new_name:
                bd.update('USER', 'name', new_name, message.from_user.id)
                bot.send_message(message.from_user.id, f"Ваше имя изменено на {new_name}")
                bot.send_message(message.from_user.id, get_profile(message.from_user.id))
                bd.update('USER', 'Q', '3', message.from_user.id)
            else:
                bot.send_message(message.from_user.id, "Пожалуйста, введите имя.")
    else:
        while bd.get_info("USER", "id", message.from_user.id, "*")[0][2] == '0':

            try:
                number = int(message.text)
                if 0 < number <= len(set(bd.get_all("QUIZ", 'Quiz_id'))):
                    quiz_done = bd.get_info("USER", "id", message.from_user.id, "*")[0][6]
                    if str(number) in quiz_done:
                        bot.send_message(message.from_user.id, 'Вы уже прошли данный квиз!')
                        bot.send_message(message.chat.id, 'Хотите выбрать квиз заново?\n /Continue\n /Stop')
                        bd.update('USER', 'Q', '1', message.from_user.id)
                    else:
                        Quiz_start(message.text, message.from_user.id)
                        bd.update('USER', 'Q', '1', message.from_user.id)
                else:
                    bot.send_message(message.chat.id, 'Quiz под данным номером не существует!')
                    bot.send_message(message.chat.id, 'Хотите выбрать квиз заново?\n /Continue\n /Stop')
                    bd.update('USER', 'Q', '1', message.from_user.id)
            except ValueError:
                bot.send_message(message.chat.id, 'Вы ввели не число!')
                bot.send_message(message.chat.id, 'Хотите выбрать квиз заново?\n /Continue\n /Stop')
                bd.update('USER', 'Q', '1', message.from_user.id)


def quiz_choose(message):
    if message.text == '/Continue':
        bot.send_message(message.from_user.id, 'Введи номер квиза:')
        bd.update('USER', 'Q', '0', message.from_user.id)
    elif message.text == '/Stop':
        bot.send_message(message.from_user.id, 'Если захотите пройти квиз, то используйте команду /Quiz')
        bd.update('USER', 'Q', '0', message.from_user.id)


def Quiz_start(message, id):
    base_info = bd.get_info("QUIZ", "Quiz_id", message, "*")
    bd.update('USER', 'Quiz_id', message, id)

    if base_info:
        q_poz = int(bd.get_info("USER", "id", id, "*")[0][3])
        quiz_data = base_info[q_poz]

        bot.send_message(id, quiz_data[2], reply_markup=create_question(base_info, id))
    else:
        bot.send_message(id, 'Квиз не найден!')


def create_question(base_info, id):
    q_poz = int(bd.get_info("USER", "id", id, "*")[0][3])

    quiz_data = base_info[q_poz]

    buttons = [
        types.InlineKeyboardButton(text=quiz_data[3], callback_data=f'{quiz_data[3]},N'),
        types.InlineKeyboardButton(text=quiz_data[4], callback_data=f'{quiz_data[4]},N'),
        types.InlineKeyboardButton(text=quiz_data[5], callback_data=f'{quiz_data[5]},N'),
        types.InlineKeyboardButton(text=quiz_data[6], callback_data=f'{quiz_data[6]},N')
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for button in buttons:
        keyboard.add(button)

    return keyboard


def next_question(base_info, id):
    q_poz = int(bd.get_info("USER", "id", id, "*")[0][3])

    quiz_data = base_info[q_poz]

    # Создаем кнопки ответов для следующего вопроса
    buttons = [
        types.InlineKeyboardButton(text=quiz_data[3], callback_data=f'{quiz_data[3]},N'),
        types.InlineKeyboardButton(text=quiz_data[4], callback_data=f'{quiz_data[4]},N'),
        types.InlineKeyboardButton(text=quiz_data[5], callback_data=f'{quiz_data[5]},N'),
        types.InlineKeyboardButton(text=quiz_data[6], callback_data=f'{quiz_data[6]},N')
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for button in buttons:
        keyboard.add(button)

    return quiz_data, keyboard


@bot.callback_query_handler(lambda call: True)
def handle_callback(call):
    try:
        q_choose = int(bd.get_info("USER", "id", call.from_user.id, "*")[0][4])
        base_info = bd.get_info("QUIZ", "Quiz_id", q_choose, "*")

        q_poz = int(bd.get_info("USER", "id", call.from_user.id, "*")[0][3])
        quiz_data = base_info[q_poz]

        data = call.data.split(',')
        user_answer = data[0]
        flag = str(data[1]) if len(data) > 1 else ''

        if flag == 'N':
            if user_answer == quiz_data[7]:
                result_text = "Верно!"
                points = int(bd.get_info("USER", "id", call.from_user.id, "*")[0][5]) + 1
                bd.update('USER', 'Now_points', points, call.from_user.id)
                bd.update('USER', 'Quiz_points', points, call.from_user.id)
            else:
                result_text = "Не верно!"

            # Создаем кнопку "Дальше"
            next_button = types.InlineKeyboardButton(text="Дальше", callback_data=f"{call.from_user.id},NEXT")

            # Отправляем сообщение с результатом и кнопкой "Дальше"
            bot.edit_message_text(
                text=f"{result_text}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=types.InlineKeyboardMarkup().add(next_button)
            )
        elif flag == "NEXT":  # Обработка нажатия на кнопку "Дальше"
            if q_poz + 1 < len(base_info):
                bd.update('USER', 'q_poz', q_poz + 1, call.from_user.id)
                quiz_data, next_keyboard = next_question(base_info, call.from_user.id)

                # Отправляем сообщение с новым вопросом и кнопками ответов
                bot.edit_message_text(
                    text=f"{quiz_data[2]}?",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=next_keyboard
                )
            else:
                # Последний вопрос пройден
                bot.edit_message_text(
                    text="Вы прошли квиз!",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
                correct_answers = bd.get_info("USER", "id", call.from_user.id, "*")[0][7]
                bot.send_message(call.from_user.id,
                                 f"Правильные ответы: {correct_answers} из {len(base_info)}"
                                 "Если хотите пройти еще квиз, напишите /Continue\n"
                                 "Если хотите посмотреть доступные команды, напишите /help")
                quiz_done = str(bd.get_info("USER", "id", call.from_user.id, "*")[0][6])
                quiz_done = quiz_done + str(bd.get_info("USER", "id", call.from_user.id, "*")[0][4]) + ','
                bd.update('USER', 'Quiz_done', quiz_done, call.from_user.id)
                bd.update('USER', 'Q', '0', call.from_user.id)
                bd.update('USER', 'Quiz_id', '0', call.from_user.id)
                bd.update('USER', 'Now_points', '0', call.from_user.id)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Произошла ошибка при обработке вашего запроса.")

    except Exception as e:
        print(f"Ошибка в handle_callback: {e}")
        bot.answer_callback_query(callback_query_id=call.id, text="Произошла ошибка.")


def get_profile(id):
    profile_info = bd.get_info("USER", "id", id, "*")
    if profile_info:
        name = profile_info[0][1]
        points = profile_info[0][5]
        return f"Вот твой профиль:\nИмя: {name}\nСчет: {points}"
    else:
        return "Профиль не найден"


if __name__ == '__main__':
    bd.start_bd()
    try:
        bd.create_bd()
    except:
        print("\033[35m {}".format('DB already exists!'))

    bot.polling(skip_pending=True)
