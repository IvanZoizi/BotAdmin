from telebot import types


def none():
    return types.ReplyKeyboardRemove()


def create_keyboard(btn_lines):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for line in btn_lines:
        btn_arr = []
        for name in line:
            btn_arr.append(types.KeyboardButton(text=name))
        keyboard.add(*btn_arr)
    return keyboard


def create_inline_keyboard(btn_lines):
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    for line in btn_lines:
        btn_arr = []
        for name, data in line:
            btn_arr.append(types.InlineKeyboardButton(text=name, callback_data=data))
        keyboard.add(*btn_arr)
    return keyboard


def back():
    return create_keyboard([
        ['<< Назад']
    ])


def add_group(is_agree):
    if not is_agree:
        return create_keyboard([
            ['Добавить группу'],
            ['Админ-панель']
        ])
    else:
        return create_keyboard([
            ['Добавить группу'],
            ['Админ-панель'],
            ['<< Назад']
        ])


def add_group_continue():
    return create_keyboard([
        ['Продолжить'],
        ['Добавить еще группу']
    ]) 


def is_agree():
    return create_keyboard([
        ['Я согласен']
    ])


def menu(is_agree):
    if is_agree:
        return create_keyboard([
            ['Перейти в личный кабинет'],
            ['Добавить группу'],
            ['Админ-панель']
        ])
    else:
        return create_keyboard([
            ['Добавить группу'],
            ['Админ-панель']
        ])


def account_menu():
    return create_keyboard([
        ['Вывести средства'],
        ['<< Назад']
    ])


def payout_agree(from_user_id, amount, is_agreed=False):
    return create_inline_keyboard([
        [('Подтвердить ' + '✅' * is_agreed, f'payout_agree|{from_user_id}:{amount}')]
    ])


def adm_panel():
    return create_keyboard([
        ['Выплатить % пользователю'],
        ['Изменить пароль Админ-панели'],
        ['Изменить начальный текст'],
        ['<< Назад']
    ])


def pay_user_list(users_list):
    return create_inline_keyboard([
        [(user.username, f'pay_user_list|{user.id}') for user in users_list]
    ])


def pay_user(user_id):
    return create_inline_keyboard([
        [('Выплатить', f'pay_user|{user_id}')]
    ])