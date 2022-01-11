from Classes.Facts import Facts
from Classes.Level import Level
from Classes.Games import PuzzleGame, TranslatorGame, MixGame, Game
from Classes.Lectures import Lectures, data
from Classes.Recomendations import get_recommend
from Classes.Test import Test
from transliterate.decorators import transliterate_function
from Classes.BotWithUsers import BotWithPages
from keyboards import MainKeyboard

from Classes.constants import winning_score, max_message_length

bot = BotWithPages('token')


@bot.message_handler(commands="start")
def cmd_start(message):
    """Function to handle the /start command"""
    bot.reply_to(message, "Привіт, " + message.from_user.first_name + "! Я - бот для вивчення англійської.")
    bot.send_message(message.from_user.id, "Оберіть з наступних опцій:", reply_markup=[MainKeyboard.keyboard])
    bot.set_user(message.from_user.id)


@bot.message_handler(commands="help")
def cmd_help(message):
    """Function to handle the /help command"""
    bot.reply_to(message, "Введіть /start для початку роботи.")


@bot.message_handler(func=lambda mes: True)
def correct_cmd(message):
    """Function to handle normal text"""
    if bot.get_user(message.from_user.id):
        if message.text == "Ігри":
            bot.get_user(message.from_user.id).page = None
            bot.send_message(message.from_user.id, "Обери гру:", reply_markup=[Game.get_keyboard()])
        elif message.text == "Лекції":
            bot.get_user(message.from_user.id).page = None
            bot.send_message(message.from_user.id, "Оберіть з наступних лекцій:",
                             reply_markup=[Lectures.get_keyboard(bot.get_user(message.chat.id).number)])
        elif message.text == "Що подивитись/почитати?":
            bot.get_user(message.from_user.id).page = bot.get_user(message.from_user.id).level
            bot.send_message(message.from_user.id, "Ти знаєш свій рівень англійської?" if
            bot.get_user(message.from_user.id).page.level == "None" else "Меню",
                             reply_markup=[bot.get_user(message.from_user.id).level.keyboard])
        elif message.text == "Тести":
            bot.get_user(message.from_user.id).page = None
            bot.send_message(message.from_user.id, "Дай 5 правильних відповідей і дізнайся цікавий факт",
                             reply_markup=[Test.get_keyboard()])
        else:
            if issubclass(type(bot.get_user(message.chat.id).page), Game):
                if bot.get_user(message.chat.id).page.set_answer(message.text):
                    bot.get_user(message.chat.id).page.stop(True)
                else:
                    bot.send_message(message.chat.id, 'На жаль, відповідь не правильна(')
            elif issubclass(type(bot.get_user(message.chat.id).page), Level):
                level = translate(message.text)
                if level in ["A1", "A2", "B1", "B2", "C1"]:
                    bot.get_user(message.chat.id).level = level
                    bot.send_message(message.chat.id, "Ваш рівень: " + level)
                    bot.send_message(message.from_user.id, "Що ви хочете отримати?:",
                                     reply_markup=[bot.get_user(message.chat.id).level.keyboard])
                else:
                    bot.send_message(message.chat.id, "Неправильно введений рівень")
                    bot.send_message(message.chat.id, "Введіть ваш рівень англійської: ")
            elif issubclass(type(bot.get_user(message.chat.id).page), Test):
                answer_quest = message.text
                bot.send_message(message.chat.id, bot.get_user(message.chat.id).page.passing_test(answer_quest))
                bot.get_user(message.chat.id).page.next_task()
                if not bot.get_user(message.chat.id).page.index:
                    bot.get_user(message.chat.id).score += 1
                if bot.get_user(message.chat.id).page.sentence and (
                        bot.get_user(message.chat.id).page.index or bot.get_user(message.chat.id).score
                        < winning_score):
                    bot.send_message(message.chat.id, str(bot.get_user(message.chat.id).page))
                    bot.send_message(message.chat.id, "Введіть відповідь: ")
                else:
                    bot.get_user(message.chat.id).add_score(bot.get_user(message.chat.id).page.score)
                    bot.get_user(message.chat.id).page.stop()
                    bot.send_message(message.from_user.id, f'Тест завершено')
                    bot.send_message(message.from_user.id,
                                     f'Ваш рахунок: {bot.get_user(message.chat.id).page.score}')
                    if not bot.get_user(message.chat.id).page.index:
                        if bot.get_user(message.chat.id).page.score >= winning_score:
                            bot.send_message(message.chat.id, f"Fun fact: {Facts()}")
                    else:
                        if bot.get_user(message.chat.id).page.score >= winning_score:
                            bot.send_message(message.chat.id, f"Fun fact: {Facts()}")
                    bot.get_user(message.chat.id).page = None
            else:
                bot.reply_to(message, "Не можу зрозуміти Ваше повідомлення.\n Введіть /help.")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    """Function is called when the button is pressed"""
    if bot.get_user(call.from_user.id):
        dict_game = {"cipher": MixGame, "translate": TranslatorGame, "riddles": PuzzleGame}
        if bot.get_user(call.from_user.id).page:
            if issubclass(type(bot.get_user(call.from_user.id).page), Game):
                if call.data == 'start':
                    bot.get_user(call.from_user.id).page.start()
                elif call.data == 'rules':
                    bot.send_message(call.from_user.id, str(bot.get_user(call.from_user.id).page))
                elif call.data == 'difficulty':
                    bot.get_user(call.from_user.id).page.change_difficulty()
                elif call.data == 'back':
                    bot.get_user(call.from_user.id).page = None
                    bot.send_message(call.from_user.id, 'Обери гру: ', reply_markup=[Game.get_keyboard()])
            elif issubclass(type(bot.get_user(call.from_user.id).page), Lectures):
                if call.data == 'back':
                    bot.get_user(call.from_user.id).page = None
                    bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=[
                        Lectures.get_keyboard(bot.get_user(call.from_user.id).number)])
                elif call.data == 'test':
                    bot.get_user(call.from_user.id).page = Test(bot, call.from_user.id,
                                                                bot.get_user(call.from_user.id).page.index)
                    bot.send_message(call.from_user.id, str(bot.get_user(call.from_user.id).page))
                    bot.send_message(call.from_user.id, "Введіть відповідь: ")
            elif issubclass(type(bot.get_user(call.from_user.id).page), Level):
                if call.data == 'up':
                    bot.get_user(call.from_user.id).level.up_level()
                    bot.send_message(call.from_user.id, "Ваш рівень: " + bot.get_user(call.from_user.id).level.level)
                elif call.data == 'down':
                    bot.get_user(call.from_user.id).level.down_level()
                    bot.send_message(call.from_user.id, "Ваш рівень: " + bot.get_user(call.from_user.id).level.level)
                elif call.data == "answer":
                    bot.send_message(call.from_user.id, "Введіть ваш рівень англійської: ")
                elif call.data == 'book' or call.data == 'film':
                    recommend = get_recommend(call.data, bot.get_user(call.from_user.id).level.level)
                    bot.send_photo(call.from_user.id, recommend.image(), caption=recommend.description())
        elif call.data == "tests":
            setattr(bot.get_user(call.from_user.id), 'score', 0)
            bot.get_user(call.from_user.id).page = Test(bot, call.from_user.id, 0)
            bot.send_message(call.from_user.id, str(bot.get_user(call.from_user.id).page))
            bot.send_message(call.from_user.id, "Введіть відповідь: ")
        elif call.data in dict_game:
            bot.get_user(call.from_user.id).page = dict_game[call.data](bot, call.from_user.id)
        elif call.data in data.keys():
            bot.get_user(call.from_user.id).page = Lectures(call.data)
            if len(str(bot.get_user(call.from_user.id).page)) > max_message_length:
                for x in range(0, len(str(bot.get_user(call.from_user.id).page)), max_message_length):
                    bot.send_message(call.from_user.id,
                                     str(bot.get_user(call.from_user.id).page)[x:x + max_message_length])
            else:
                bot.send_message(call.from_user.id, str(bot.get_user(call.from_user.id).page))
            bot.send_photo(call.from_user.id, bot.get_user(call.from_user.id).page.image)
            bot.send_message(call.from_user.id, "Для засвоєння матеріалу пройдіть короткий тест за темою лекції",
                             reply_markup=[bot.get_user(call.from_user.id).page.keyboard])
        elif call.data == "◀":
            bot.get_user(call.from_user.id).number -= 1
            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id,
                                          reply_markup=[Lectures.get_keyboard(bot.get_user(call.from_user.id).number)])
        elif call.data == "▶":
            bot.get_user(call.from_user.id).number += 1
            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id,
                                          reply_markup=[Lectures.get_keyboard(bot.get_user(call.from_user.id).number)])
    else:
        bot.send_message(call.from_user.id, 'напишіть /start')


@transliterate_function(language_code='ru', reversed=True)
def translate(text):
    """Decorator for transliterate user's message"""
    return text.upper()
