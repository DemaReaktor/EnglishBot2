import json
import math
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

with open("jsonFiles/lectures.json", 'r', encoding="utf-8") as file:
    data = json.load(file)


class Lectures:
    def __init__(self, lecture: int or None = None):
        self.name = data[lecture]["name"]
        self.text = data[lecture]["text"]
        self.image = data[lecture]["image"]
        self.audio = None
        self.test = "test"
        self.index = int(lecture)
        self.keyboard = InlineKeyboardMarkup()
        self.keyboard.add(InlineKeyboardButton(text='Розпочати', callback_data='test'))
        self.keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back'))

    def __str__(self):
        return f'\b{self.name}\b\n\n{self.text}'

    @classmethod
    def get_keyboard(cls, number: int) -> InlineKeyboardMarkup:
        if not isinstance(number, int):
            raise TypeError('number should have type "int"')
        count = math.ceil(float(data.__len__()) / 5)
        while number < 0:
            number += count
        while number >= count:
            number -= count
        keyboard = InlineKeyboardMarkup()
        for index in range(5):
            if number * 5 + index < data.__len__():
                keyboard.add(InlineKeyboardButton(data[str(index + number * 5 + 1)]['name'],
                                                  callback_data=str(index + number * 5 + 1)))
        keyboard.add(*[InlineKeyboardButton(name, callback_data=name) for name in ['◀', '▶']])
        return keyboard

