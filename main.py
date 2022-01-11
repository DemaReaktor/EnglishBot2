from telebot import TeleBot
from dispatcher import dp
import handlers
from handlers.personal_actions import bot

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
