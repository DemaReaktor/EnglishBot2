from aiogram import types
from dispatcher import dp
import config
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

bot = BotWithPages(config.BOT_TOKEN)

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

@transliterate_function(language_code='ru', reversed=True)
def translate(text):
    """Decorator for transliterate user's message"""
    return text.upper()
