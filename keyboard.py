from telebot import types


week_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


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


def yes_no():
    return create_keyboard([
        ['Да', 'Нет'],
        ['<< Назад']
    ])


def menu():
    return create_keyboard([
        ['Начать рассылку'],
        ['Запланированные публикации'],
        ['Настройки']
    ])


def back():
    return create_keyboard([
        ['<< Назад']
    ])


def inline_close():
    return create_inline_keyboard([
        [('<< Закрыть', 'del_msg:None')]
    ])


def settings():
    return create_keyboard([
        ['Изменить пароль бота'],
        ['Добавить группу/канал'],
        ['Удалить группу/канал'],
        ['<< Назад']
    ])


def groups_ids_del(ids, chat_titles):
    return create_inline_keyboard([
        [(f'{chat_titles[i]}', 'None'), ('🗑️', f'del:{ids[i]}')] for i in range(len(ids))
    ])


def chat_choose(ids, choose_list, chat_titles):
    return create_inline_keyboard([
        [(f'{chat_titles[i][:30]}... {"✅" * choose_list[i] + "❌" * (not choose_list[i])}', f'choose:{ids[i]}')] for i in range(len(ids))
    ] + [[('Выбрать все', 'choose:all')], [('Готово', 'choose:done')]])


def choose_sender_type():
    return create_keyboard([
        ['Разместить сейчас'],
        ['Запланировать публикацию'],
        ['<< Назад']
    ])


def later_msgs_list(msgs):
    keyboard_list = list()
    for msg in msgs:

        if msg is None:
            continue
            
        if 'is_pinned' not in msg:
            msg['is_pinned'] = False
        
        week_days_str = ', '.join([week_days[i] for i in msg["week_days"]])
        hour, minute, second = msg['time_pub']
        if len(str(minute)) < 2:
            minute = '0' + str(minute)
        if len(str(hour)) < 2:
            hour = '0' + str(hour)

        try:
            endpoint_day, endpoint_month, endpoint_year = msg['endpoint_date'].day, msg['endpoint_date'].month, msg['endpoint_date'].year
            if len(str(endpoint_day)) < 2:
                endpoint_day = '0' + str(endpoint_day)
            if len(str(endpoint_month)) < 2:
                endpoint_month = '0' + str(endpoint_month)
            endpoint_date = str(endpoint_day) + '.' + str(endpoint_month) + '.' + str(endpoint_year)
        except:
            endpoint_date = '-'
        
        keyboard_list.append([
            (str(len(keyboard_list) + 1) +
              ' - ' + msg['post_name'], f'later_msg_get:{msg["start_time"]}'), #+ ' - ' + 
              # f'{week_days_str} {hour}:{minute}', f'later_msg_get:{msg["start_time"]}'),
            ('✏️', f'later_msg_edit:{msg["start_time"]}'),
            (f'📍{"✅" * msg["is_pinned"]}', f'later_msg_pin:{msg["start_time"]}'),
            ('🗑️', f'later_msg_del:{msg["start_time"]}'),
            (f'{endpoint_date}', f'later_msg_get:{msg["start_time"]}')
        ])
        # keyboard_list.append([(f'{week_days_str} {hour}:{minute}', f'later_msg_get:{msg["start_time"]}'),
        #                        ('✏️', f'later_msg_edit:{msg["start_time"]}'),
        #                        ('🗑️', f'later_msg_del:{msg["start_time"]}')])
    
    return create_inline_keyboard(keyboard_list)


def week_days_choose(week_days_chosen):
    return create_inline_keyboard([
        [(f'{week_days[i]} {"✅" * (i in week_days_chosen)}', f'week_days_choose:{i}') for i in range(len(week_days))]
    ] + [[('Выбрать все', 'week_days_choose:all')], [('Готово', 'week_days_choose:done')]])


def edit_week_days_choose(msg_start_time, week_days_chosen):
    return create_inline_keyboard([
        [(f'{week_days[i]} {"✅" * (i in week_days_chosen)}', f'edit_week_days_choose:{i}:{msg_start_time}') for i in range(len(week_days))]
    ] + [[('Выбрать все', f'edit_week_days_choose:all:{msg_start_time}')], [('Готово', f'edit_week_days_choose:done:{msg_start_time}')]])


def edit_chat_choose(msg_start_time, ids, choose_list, chat_titles):
    return create_inline_keyboard([
        [(f'{chat_titles[i][:30]}... {"✅" * choose_list[i] + "❌" * (not choose_list[i])}', f'edit_choose:{ids[i]}:{msg_start_time}')] for i in range(len(ids))
    ] + [[('Выбрать все', f'edit_choose:all:{msg_start_time}')], [('Готово', f'edit_choose:done:{msg_start_time}')]])


def later_msg_edit_choose():
    return create_keyboard([
        ['Изменить название публикации'],
        ['Изменить текст публикации'],
        ['Изменить дату и время публикации'],
        ['Изменить выбранные группы'],
        ['Изменить конечную дату публикации'],
        ['<< Назад']
    ])


def back_continue():
    return create_keyboard([
        ['Пропустить'],
        ['<< Назад']
    ])


def later_msg_time_choose(time_week_days):
    time_week_arr = list()
    for wd_key in time_week_days:
        hour, minute = time_week_days[wd_key][:2]
        if len(str(minute)) < 2:
            minute = '0' + str(minute)
        if len(str(hour)) < 2:
            hour = '0' + str(hour)
        time_week_arr.append((f'{week_days[int(wd_key)]} {hour}:{minute}', f'time_week_days_choose:{wd_key}'))
    return create_inline_keyboard([
        time_week_arr,
        [('Готово', 'time_week_days_choose:done')],
        [('Пропустить >>', 'time_week_days_choose:continue')]
    ])


def edit_later_msg_time_choose(time_week_days, msg_start_time):
    time_week_arr = list()
    for wd_key in time_week_days:
        hour, minute = time_week_days[wd_key][:2]
        if len(str(minute)) < 2:
            minute = '0' + str(minute)
        if len(str(hour)) < 2:
            hour = '0' + str(hour)
        time_week_arr.append((f'{week_days[int(wd_key)]} {hour}:{minute}', f'edit_time_week_days_choose:{wd_key}:{msg_start_time}'))
    return create_inline_keyboard([
        time_week_arr,
        [('Готово', f'edit_time_week_days_choose:done:{msg_start_time}')],
        [('Пропустить >>', f'edit_time_week_days_choose:continue:{msg_start_time}')]
    ])