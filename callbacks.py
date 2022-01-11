from aiogram import types
from dispatcher import dp
import config
from handlers.personal_actions import bot
from Classes.Facts import Facts
from Classes.Level import Level
from Classes.Games import PuzzleGame, TranslatorGame, MixGame, Game
from Classes.Lectures import Lectures, data
from Classes.Recomendations import get_recommend
from Classes.Test import Test
from Classes.constants import winning_score, max_message_length


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
