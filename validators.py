from typing import Optional

MAX_STICKERS = 50

def validate_amount(text: str, mode:str) -> (str, Optional[int]):
    try:
        amount = int(text)
    except (TypeError, ValueError):
        return ('Количество стикеров должно быть числом. Введите корректное число стикеров.', 'notanum')
    if amount <= 0 :
        return ('Количество стикеров должно быть больше нуля. Введите корректное число стикеров.', 'less0')
    if (amount > MAX_STICKERS) & (mode=="Попросить"):
        return (f'Нельзя попросить больше чем {MAX_STICKERS} стикеров. Введите меньшее число.', 'toobig')

    return ('true', amount)

def padezh(amount: int):
    if (amount % 10 == 1):
        return 'cтикер'
    if (amount % 10 == 0):
        return 'cтикеров'
    elif (amount % 10 < 5):
        return 'стикера'
    elif (amount % 10 >= 5):
        return 'стикеров'
    else:
        return 'стикеров'


def validate_phone(text: str) -> Optional[int]:
    if len(text) != 8:
        return ('Неверный формат телефона. Введите номер в формате 99123456', 'lenthnot8')
    try:
        phone = int(text)
    except (TypeError, ValueError):
        return ('Неверный формат телефона. Введите номер в формате 99123456','notanum')
    if phone <= 0 :
        return ('Неверный формат телефона. Введите номер в формате 99123456','less0')

    return ('true', phone)