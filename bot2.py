# -*- coding: utf-8 -*-
# Written by M1x7urk4
#
#
# █───█──█─██─██─████─█─█─████─█──█─█───
# ██─██─██──███──█──█─█─█─█──█─█─█──█──█
# █─█─█──█───█─────██─█─█─████─██───████
# █───█──█──███───██──█─█─█─█──█─█─────█
# █───█──█─██─██─██───███─█─█──█──█────█


# Import libraries ------------------------------------------------------------

from collections import defaultdict
import config

import keyboard2
from telebot import TeleBot

from datetime import datetime

# -----------------------------------------------------------------------------


class Date:
    def __init__(self, date):
        self.date = date
    

    def __str__(self):
        year, month, day = self.date.year, self.date.month, self.date.day
        hour, minute = self.date.hour, self.date.minute
        
        if len(str(month)) == 1:
            month = '0' + str(month)
        else:
            month = str(month)
        
        if len(str(day)) == 1:
            day = '0' + str(day)
        else:
            day = str(day)
        
        if len(str(hour)) == 1:
            hour = '0' + str(hour)
        else:
            hour = str(hour)

        if len(str(minute)) == 1:
            minute = '0' + str(minute)
        else:
            minute = str(minute)
        
        return f'{day}.{month}.{year}'


class User:
    def __init__(self, id, username=None, is_agree=False, balance=0, user_groups=list()):
        self.id = id
        self.username = username
        self.is_agree = is_agree
        self.balance = balance
        self.user_groups = user_groups


class Bot2:
    def __init__(self):
        self.bot = TeleBot(token=config.ACCESS_TOKEN_2)
        self.users = list()
        self.group_ids = list()
        
        self.admin_list = [5589463177]

        self.MIN_OUT_BALANCE = 10000
        self.OUT_CHANNEL_ID = -1001731857984
        self.adm_panel_password = '1234'

        self.start_text = 'Если Вы нажимаете ниже кнопку "Я согласен", то даете нашему боту разрешение на публикацию рекламы в Вашей группе. Вы получаете ....% (??) от любого дохода полученного за счет размещения рекламных постов в Вашей группе. Доход будет начисляться автоматически, и Вы сможете увидеть его в личном кабинете в нашем боте.'
    
    # Check if 'x' is a number -> bool
    def is_num(self, x):
        try:
            x = float(x)
            return True
        except:
            return False
    
    # Find the user from all users in this bot -> User/None
    def find_user(self, user_id):
        for user in self.users:
            if str(user.id) == str(user_id):
                return user
        return None
    

    def start(self, main_bot):

        print('[LOG] Bot2 - started')

        @self.bot.message_handler(commands=['start'])
        def start_msg(message):
            if message.chat.type != 'private':
                return

            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if cur_user is None:
                cur_user = User(message.chat.id, message.from_user.username)
                self.users.append(cur_user)
            
            if not cur_user.is_agree:
                self.bot.send_message(chat_id=message.chat.id,
                                    text='Добрый день!\n\nСпасибо, что решили присоединиться к нашей сети групп.\nДля добавления свой группы следуйте, пожалуйста, нашим инструкциям:\n\n1) Добавьте этого бота https://t.me/MoyParthner_bot  в администраторы добавляемой группы/канала\n\n2) Добавьте в администраторы группы/канала бота https://t.me/Moy_Admin_Group_Bot\n\n3) Далее сообщите этому боту ID Вашей группы/канала\nДля получения ID Вы можете воспользоваться ботом https://t.me/username_to_id_bot либо любым другим общедоступным ресурсом',
                                    reply_markup=keyboard2.add_group(cur_user.is_agree))
            else:
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))


        @self.bot.message_handler(commands=['adm_panel'])
        def adm_panel_handle(message):
            if message.chat.type != 'private':
                return

            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.chat.id not in self.admin_list:
                self.bot.send_message(chat_id=message.chat.id,
                                      text='Доступ запрещен!',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))
                return
        
            msg = self.bot.send_message(chat_id=message.chat.id,
                                  text='== Админ-панель ==',
                                  reply_markup=keyboard2.adm_panel())
            self.bot.register_next_step_handler(msg, adm_panel)


        @self.bot.message_handler(content_types=['text'])
        def text_handle(message):
            if message.chat.type != 'private':
                return
            
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if cur_user is None:
                cur_user = User(message.chat.id, message.from_user.username)
                self.users.append(cur_user)

                self.bot.send_message(chat_id=message.chat.id,
                                    text='Добрый день!\n\nСпасибо, что решили присоединиться к нашей сети групп.\nДля добавления свой группы следуйте, пожалуйста, нашим инструкциям:\n\n1) Добавьте этого бота https://t.me/MoyParthner_bot  в администраторы добавляемой группы/канала\n\n2) Добавьте в администраторы группы/канала бота https://t.me/Moy_Admin_Group_Bot\n\n3) Далее сообщите этому боту ID Вашей группы/канала\nДля получения ID Вы можете воспользоваться ботом https://t.me/username_to_id_bot либо любым другим общедоступным ресурсом',
                                    reply_markup=keyboard2.add_group(cur_user.is_agree))
                return

            if message.text == 'Добавить группу':

                if not cur_user.is_agree:
                    kbrd = keyboard2.none 
                else:
                    kbrd = keyboard2.back

                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Введите ID группы:',
                                      reply_markup=kbrd())
                self.bot.register_next_step_handler(msg, add_group)
            elif message.text == 'Перейти в личный кабинет' and cur_user.is_agree:
                today = Date(datetime.now())
                group_names = ", ".join([self.bot.get_chat(int(id)).title for id in cur_user.user_groups])
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text=f'== Личный кабинет ==\n\n- Дата: {today}\n- Баланс: {cur_user.balance}₽\n\nВаши группы: {group_names}',
                                            reply_markup=keyboard2.account_menu())
                self.bot.register_next_step_handler(msg, account_menu)
            elif message.text == 'Админ-панель':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Введите пароль от Админ-панели:',
                                            reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, adm_panel_enter)
            else:
                self.bot.send_message(chat_id=message.chat.id,
                                      text='Неизвестная команда!',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))
        

        @self.bot.callback_query_handler(func=lambda x: True)
        def callback_handle(call):
            if call.message.chat.type != 'private':
                return
            
            prefix, data = call.data.split('|')

            if prefix == 'payout_agree':
                data, amount = data.split(':')
                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                   message_id=call.message.id,
                                                   reply_markup=keyboard2.payout_agree(data, amount, True))
                
                from_user = self.find_user(data)
                from_user.balance -= float(amount)
                self.bot.send_message(chat_id=int(data),
                                      text=f'Заявка на вывод подтверждена!\nСкоро средства поступят на указанные Вами реквизиты.\nСумма вывода: {amount} руб')
            elif prefix == 'pay_user_list':
                user = self.find_user(data)
                try:
                    groups_info = main_bot.find_user(data).chats_info

                    groups_info_text = ''
                    for group_id in groups_info:
                        group_msg_cnt = defaultdict(int)
                        for msg_date in groups_info[group_id]:
                            date = str(Date(msg_date))
                            group_msg_cnt[date] += 1
                        
                        group_date_info_text = ''
                        for date in group_msg_cnt:
                            group_date_info_text += f'- {date} - кол-во постов: {group_msg_cnt[date]}\n'
                        
                        groups_info_text += f'Название: {self.bot.get_chat(int(group_id)).title}\nКол-во (по дате):\n{group_date_info_text}\n\n'

                except:
                    groups_info_text = ''
                self.bot.edit_message_text(chat_id=call.message.chat.id,
                                           message_id=call.message.id,
                                           text=f'== Информация о пользователе ==\n\n- ID: {user.id}\n- Имя: @{user.username}\n- Баланс: {user.balance}\n- Публикации:\n\n{groups_info_text}',
                                           reply_markup=keyboard2.pay_user(user.id))
            elif prefix == 'pay_user':
                msg = self.bot.send_message(chat_id=call.message.chat.id,
                                       text='Введите сумму выплаты (руб):',
                                       reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, pay_user, data)


# ---- Next-step handlers -----------------------------------------------------

        def add_group(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == 'Админ-панель':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Введите пароль от Админ-панели:',
                                            reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, adm_panel_enter)
                return
            
            if message.text in cur_user.user_groups:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Эта группа уже добавлена!\nВведите ID группы повторно:',
                                      reply_markup=keyboard2.add_group_continue())
                self.bot.register_next_step_handler(msg, add_group_continue)
            elif self.is_num(message.text):
                try:
                    self.bot.get_chat(int(message.text)).title

                    if message.text not in self.group_ids:
                        self.group_ids.append(message.text)
                        main_bot.chat_ids.append(message.text)
                    
                    cur_user.user_groups.append(message.text)
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Спасибо, Ваша группа добавлена!',
                                        reply_markup=keyboard2.add_group_continue())
                    self.bot.register_next_step_handler(msg, add_group_continue)
                except:
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='Ошибка!\nГруппа не может быть добавлена:\n1) Проверьте корректность ID группы\n2) Проверьте, что бот добавлен в админы группы\n\nВведите ID группы повторно:',
                                        reply_markup=keyboard2.back())
                    self.bot.register_next_step_handler(msg, add_group)
            elif message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Неправильный ID!\nВведите ID группы повторно:',
                                      reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, add_group)
        

        def add_group_continue(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == 'Продолжить':
                if not cur_user.is_agree:
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                                text=self.start_text,
                                                reply_markup=keyboard2.is_agree())
                    self.bot.register_next_step_handler(msg, is_agree)
                else:
                    self.bot.send_message(chat_id=message.chat.id,
                                          text='== Главное меню ==',
                                          reply_markup=keyboard2.menu(cur_user.is_agree))
            elif message.text == 'Добавить еще группу':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Введите ID группы:',
                                      reply_markup=keyboard2.none())
                self.bot.register_next_step_handler(msg, add_group)
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Неизвестная команда!',
                                      reply_markup=keyboard2.add_group_continue())
                self.bot.register_next_step_handler(msg, add_group_continue)
        
        
        def is_agree(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == 'Я согласен':
                cur_user.is_agree = True
                self.bot.send_message(chat_id=message.chat.id,
                                      text='Добро пожаловать в нашу сеть групп по бизнесу, финансам, инвестициям и недвижимости. Доход от размещения рекламных постов в Вашей группе будет отражаться в личном кабинете',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Неизвестная команда!',
                                      reply_markup=keyboard2.add_group_continue())
                self.bot.register_next_step_handler(msg, add_group_continue)
        

        def account_menu(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))
            elif message.text == 'Вывести средства':
                if cur_user.balance < self.MIN_OUT_BALANCE:
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                      text=f'Недостаточно средств для вывода!\nВывод можно осуществить от {self.MIN_OUT_BALANCE} руб',
                                      reply_markup=keyboard2.account_menu())
                    self.bot.register_next_step_handler(msg, account_menu)
                else:
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                                text='Введите сумму для вывода:',
                                                reply_markup=keyboard2.back())
                    self.bot.register_next_step_handler(msg, balance_out_amount)
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Неизвестная команда!',
                                      reply_markup=keyboard2.account_menu())
                self.bot.register_next_step_handler(msg, account_menu)


        def balance_out_amount(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                today = Date(datetime.now())
                group_names = ", ".join([self.bot.get_chat(int(id)).title for id in cur_user.user_groups])
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text=f'== Личный кабинет ==\n\n- Дата: {today}\n- Баланс: {cur_user.balance}₽\n\nВаши группы: {group_names}',
                                      reply_markup=keyboard2.account_menu())
                self.bot.register_next_step_handler(msg, account_menu)
            elif not self.is_num(message.text):
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Сумма должна быть числом!\nВведите сумму для вывода:',
                                            reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, balance_out_amount)
            elif float(message.text) > cur_user.balance:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Сумма превышает текущий баланс!\nВведите сумму для вывода:',
                                            reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, balance_out_amount)
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Введите реквизиты для вывода:',
                                            reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, balance_out_info, message.text)
        

        def balance_out_info(message, amount):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                today = Date(datetime.now())
                group_names = ", ".join([self.bot.get_chat(int(id)).title for id in cur_user.user_groups])
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text=f'== Личный кабинет ==\n\n- Дата: {today}\n- Баланс: {cur_user.balance}₽\n\nВаши группы: {group_names}',
                                      reply_markup=keyboard2.account_menu())
                self.bot.register_next_step_handler(msg, account_menu)
            else:
                self.bot.send_message(chat_id=self.OUT_CHANNEL_ID,
                                      text=f'== Новая заявка на вывод ==\n\n- Имя: @{message.from_user.username}\n- Сумма: {amount}\n- Реквизиты: {message.text}',
                                      reply_markup=keyboard2.payout_agree(message.chat.id, amount))
                self.bot.send_message(chat_id=message.chat.id,
                                      text=f'Заявка на вывод средств успешно создана!\nСумма для вывода: {amount} руб',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))


        def pay_user(message, user_id):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))
            elif not self.is_num(message.text):
                msg = self.bot.send_message(chat_id=message.chat.id,
                                       text='Сумма должна быть числом!\nВведите сумму выплаты (руб):',
                                       reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, pay_user, user_id)
            else:
                to_user = self.find_user(user_id)
                to_user.balance += float(message.text)

                self.bot.send_message(chat_id=message.chat.id,
                                      text='Выплата успешно совершена!',
                                      reply_markup=keyboard2.menu(cur_user.is_agree))
    
# -----------------------------------------------------------------------------

# ---- Adm-panel step handlers --------------------------------------------------------------------

        def adm_panel_enter(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                    text='== Главное меню ==',
                                    reply_markup=keyboard2.menu(cur_user.is_agree))
                return
            elif message.text != self.adm_panel_password:
                self.bot.send_message(chat_id=message.chat.id,
                                    text='Неправильный пароль!\nДоступ запрещен!',
                                    reply_markup=keyboard2.menu(cur_user.is_agree))
                return
        
            msg = self.bot.send_message(chat_id=message.chat.id,
                                text='== Админ-панель ==',
                                reply_markup=keyboard2.adm_panel())
            self.bot.register_next_step_handler(msg, adm_panel)


        def adm_panel(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                  text='== Главное меню ==',
                                  reply_markup=keyboard2.menu(cur_user.is_agree))
            elif message.text == 'Выплатить % пользователю':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Выберите пользователя:',
                                            reply_markup=keyboard2.pay_user_list(self.users))
                self.bot.register_next_step_handler(msg, adm_panel)
            elif message.text == 'Изменить пароль Админ-панели':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text=f'Старый пароль: {self.adm_panel_password}\nВведите новый пароль:',
                                            reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, adm_panel_change_password)
            elif message.text == 'Изменить начальный текст':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text=f'Старый текст: {self.start_text}\n\nВведите новый текст:',
                                            reply_markup=keyboard2.back())
                self.bot.register_next_step_handler(msg, adm_panel_change_start_text)
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Неизвестная команда!',
                                            reply_markup=keyboard2.adm_panel())
                self.bot.register_next_step_handler(msg, adm_panel)
        

        def adm_panel_change_password(message):
            if message.text == '<< Назад':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='== Админ-панель ==',
                                            reply_markup=keyboard2.adm_panel())
            else:
                self.adm_panel_password = message.text
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Пароль успешно изменен!',
                                      reply_markup=keyboard2.adm_panel())
            self.bot.register_next_step_handler(msg, adm_panel)


        def adm_panel_change_start_text(message):
            if message.text == '<< Назад':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='== Админ-панель ==',
                                            reply_markup=keyboard2.adm_panel())
            else:
                self.start_text = message.text
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Текст успешно изменен!',
                                      reply_markup=keyboard2.adm_panel())
            self.bot.register_next_step_handler(msg, adm_panel)

# -------------------------------------------------------------------------------------------------

        self.bot.infinity_polling()


# def main():
#     bot = Bot2()
#     bot.start()


# if __name__ == '__main__':
#     main()
