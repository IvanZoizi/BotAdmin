from telebot import TeleBot
from telebot.types import InputMediaPhoto, InputMediaVideo, MessageEntity
import config, keyboard

import datetime, time, threading, json

import bot2
from db import DB
from pprint import pprint


# ---- MAIN VARIABLES -----------------------------------------------------------------------------

db = DB(config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_HOST)

# -------------------------------------------------------------------------------------------------


# ---- Save to DB / Load from DB funcs ----------------------------------------------------------------------------

def load_from_db(main_bot, add_bot):
    try:
        load_data = db.get_all(config.DB_TABLE_NAME)[0][0]

        # Main bot
        users = list()
        for user_id in load_data['main_bot']['users']:
            user_dict = load_data['main_bot']['users'][user_id]
            try:
                chats_info = dict()
                for key in user_dict['chats_info']:
                    chats_info[key] = list()
                    for date in user_dict['chats_info'][key]:
                        chats_info[key].append(datetime.datetime(*date))
                users.append(User(int(user_id), 
                                user_dict['username'],
                                user_dict['is_logged'],
                                user_dict['new_msg'],
                                user_dict['chat_ids_sender'],
                                chats_info))
            except:
                users.append(User(int(user_id), 
                                user_dict['username'],
                                user_dict['is_logged'],
                                user_dict['new_msg'],
                                user_dict['chat_ids_sender'],
                                user_dict['chats_info']))
        main_bot.users = users
        main_bot.bot_password = load_data['main_bot']['bot_password']
        print(main_bot.bot_password)
        main_bot.chat_ids = load_data['main_bot']['chat_ids']
        main_bot.chat_titles = load_data['main_bot']['chat_titles']

        # Load later_msgs
        later_msgs = list()
        for msg in load_data['main_bot']['later_msgs']:
            if msg['msg_caption_entities'] is not None:
                tmp_msg = dict()
                entities = list()
                for e in msg['msg_caption_entities']:
                    entities.append(MessageEntity(e['type'], e['offset'], e['length'], e['url'], e['language'], e['user']))
                
                tmp_msg['msg_caption_entities'] = entities
                for key in msg:
                    if key != 'msg_caption_entities':
                        tmp_msg[key] = msg[key]
                later_msgs.append(tmp_msg)
            
            if msg['entities'] is not None:
                tmp_msg = dict()
                entities = list()
                for e in msg['entities']:
                    entities.append(MessageEntity(e['type'], e['offset'], e['length'], e['url'], e['language'], e['user']))
                
                tmp_msg['entities'] = entities
                for key in msg:
                    if key != 'entities':
                        tmp_msg[key] = msg[key]
                later_msgs.append(tmp_msg)
            
            if msg['endpoint_date'] is not None:
                tmp_msg = dict()
                tmp_msg['endpoint_date'] = datetime.datetime(msg['endpoint_date'][2], msg['endpoint_date'][1], msg['endpoint_date'][0])
                for key in msg:
                    if key != 'endpoint_date':
                        tmp_msg[key] = msg[key]
                later_msgs.append(tmp_msg)
            
            if msg['entities'] is None and msg['entities'] is None and msg['endpoint_date'] is None:
                later_msgs.append(msg)
            
        main_bot.later_msgs = later_msgs

        # Additional bot
        add_users = list()
        for user_id in load_data['add_bot']['users']:
            user_dict = load_data['add_bot']['users'][user_id]
            add_users.append(bot2.User(int(user_id), 
                            user_dict['username'],
                            user_dict['is_agree'],
                            user_dict['balance'],
                            user_dict['user_groups']))
        add_bot.users = add_users
        add_bot.group_ids = load_data['add_bot']['group_ids']
        add_bot.admin_list = load_data['add_bot']['admin_list']
    except Exception as ex:
        print(f'[ERROR] load from db - {ex}')


def save_loop(main_bot, add_bot):
    while True:
        time.sleep(10)
        try:
            users_dict = dict()
            for user in main_bot.users:

                # 'Chat info' convert from list[datetime] -> list[list]
                chats_info_dict = dict()
                for chat_id in user.chats_info:
                    chats_info_dict[chat_id] = list()
                    for date in user.chats_info[chat_id]:
                        try:
                            chats_info_dict[chat_id].append([date.year, date.month, date.day, date.hour, date.minute, date.second])
                        except:
                            chats_info_dict[chat_id].append(date)

                users_dict[user.id] = {
                    'username': user.username,
                    'is_logged': user.is_logged,
                    'new_msg': user.new_msg,
                    'chat_ids_sender': user.chat_ids_sender,
                    'chats_info': chats_info_dict
                }

            add_users_dict = dict()
            for user in add_bot.users:
                add_users_dict[user.id] = {
                    'username': user.username,
                    'is_agree': user.is_agree,
                    'balance': user.balance,
                    'user_groups': user.user_groups
                }

            later_msgs = list()
            for msg in main_bot.later_msgs:
                try:
                    if msg['msg_caption_entities'] is not None:
                        tmp_msg = dict()
                        entities = list()
                        for e in msg['msg_caption_entities']:
                            entities.append({
                                'language': e.language,
                                'length': e.length,
                                'offset': e.offset,
                                'type': e.type,
                                'url': e.url,
                                'user': e.user,
                            })
                        tmp_msg['msg_caption_entities'] = entities
                        for key in msg:
                            if key != 'msg_caption_entities':
                                tmp_msg[key] = msg[key]
                        later_msgs.append(tmp_msg)
                    
                    if msg['entities'] is not None:
                        tmp_msg = dict()
                        entities = list()
                        for e in msg['entities']:
                            entities.append({
                                'language': e.language,
                                'length': e.length,
                                'offset': e.offset,
                                'type': e.type,
                                'url': e.url,
                                'user': e.user,
                            })
                        tmp_msg['entities'] = entities
                        for key in msg:
                            if key != 'entities':
                                tmp_msg[key] = msg[key]
                        later_msgs.append(tmp_msg)
                    
                    if msg['endpoint_date'] is not None:
                        tmp_msg = dict()
                        tmp_msg['endpoint_date'] = [msg['endpoint_date'].day, 
                                                    msg['endpoint_date'].month, 
                                                    msg['endpoint_date'].year]
                        for key in msg:
                            if key != 'endpoint_date':
                                tmp_msg[key] = msg[key]
                        later_msgs.append(tmp_msg)
                    
                    if msg['entities'] is None and msg['msg_caption_entities'] is None and msg['endpoint_date'] is None:
                        later_msgs.append(msg)
                except:
                    continue
            for key in users_dict:
                try:
                    users_dict[key]['new_msg']['entities'] = []
                    users_dict[key]['new_msg']['endpoint_date'] = [int(i) for i in users_dict[key]['new_msg']['endpoint_date'].strftime('%Y.%m.%d').split('.')]
                except Exception as ex:
                    continue
            pprint(users_dict)
            save_data = {
                'main_bot': {
                    'bot_password': str(main_bot.bot_password),
                    'chat_ids': list(main_bot.chat_ids),
                    'chat_titles': list(main_bot.chat_titles),
                    'users': dict(users_dict),
                    'later_msgs': list(later_msgs)
                },
                'add_bot': {
                    'users': dict(add_users_dict),
                    'group_ids': list(add_bot.group_ids),
                    'admin_list': list(add_bot.admin_list),
                }
            }
            print(save_data)
            db.save_all(config.DB_TABLE_NAME, json.dumps(save_data))
        except Exception as ex:
            print(f'[ERROR] save to db - {ex}')


# -------------------------------------------------------------------------------------------------


# ---- Additional funcs ---------------------------------------------------------------------------


def is_num(x):
    try:
        x = float(x)
        return True
    except:
        return False


def wait_n_seconds(bot, user, seconds):
    while True:
        if time.time() - user.new_msg['start_time'] >= seconds:
            media_photo_arr = [InputMediaPhoto(download_file(bot, one)) for one in user.new_msg['media_photo']]
            media_video_arr = [InputMediaVideo(download_file(bot, one)) for one in user.new_msg['media_video']]
            media_arr = media_photo_arr + media_video_arr
            media_arr[-1].caption = user.new_msg['msg_caption']
            media_arr[-1].caption_entities = user.new_msg['msg_caption_entities']

            for chat_id in user.chat_ids_sender:
                msg_response = bot.bot.send_media_group(chat_id, media_arr)

                # Chat-sender info (for bot2)
                if chat_id not in user.chats_info:
                    user.chats_info[chat_id] = [datetime.datetime.today()]
                else:
                    user.chats_info[chat_id].append(datetime.datetime.today())

            bot.bot.send_message(chat_id=user.id,
                                 text='Рассылка успешно завершена!',
                                 reply_markup=keyboard.menu())
                
            for chat_id in user.chat_ids_sender:
                if user.new_msg['is_pinned']:
                    bot.bot.pin_chat_message(chat_id=chat_id,
                                             message_id=msg_response[0].id)

            user.new_msg = None

            return


def wait_n_seconds_later(bot, user, seconds, msg_to_edit=None):
    while True:
        if time.time() - user.new_msg['start_time'] >= seconds:
            media_photo_arr = [InputMediaPhoto(download_file(bot, one)) for one in user.new_msg['media_photo']]
            media_video_arr = [InputMediaVideo(download_file(bot, one)) for one in user.new_msg['media_video']]
            media_arr = media_photo_arr + media_video_arr
            media_arr[-1].caption = user.new_msg['msg_caption']
            media_arr[-1].caption_entities = user.new_msg['msg_caption_entities']

            if msg_to_edit is not None:
                bot.later_msgs.pop(bot.later_msgs.index(msg_to_edit))
                bot.later_msgs.append(user.new_msg)
                bot.bot.send_message(chat_id=user.id,
                                        text='Публикация успешно изменена!',
                                        reply_markup=keyboard.menu(),
                                        entities=user.new_msg['entities'])
            elif bot.find_msg(user.new_msg['start_time']) is None:
                bot.later_msgs.append(user.new_msg)
            
            return


def send_msg(bot, chat_id, msg, reply_markup=None):
    try:
        if msg['group_id'] is None:
            # One photo/video send
            if reply_markup is None:
                # Without keyboard
                if len(msg['media_photo']) != 0 and msg['msg_caption'] is not None:
                    msg_response = bot.bot.send_photo(chat_id=chat_id,
                                    photo=download_file(bot, msg['media_photo'][0]),
                                    caption=msg['msg_caption'],
                                    caption_entities=msg['msg_caption_entities'])
                elif len(msg['media_photo']) != 0:
                    msg_response = bot.bot.send_photo(chat_id=chat_id,
                                    photo=download_file(bot, msg['media_photo'][0]))
                elif len(msg['media_video']) != 0 and msg['msg_caption'] is not None:
                    msg_response = bot.bot.send_video(chat_id=chat_id,
                                        video=download_file(bot, msg['media_video'][0]),
                                        caption=msg['msg_caption'],
                                        caption_entities=msg['msg_caption_entities'])
                elif len(msg['media_video']) != 0:
                    msg_response = bot.bot.send_video(chat_id=chat_id,
                                        video=download_file(bot, msg['media_video'][0]))
                else:
                    msg_response = bot.bot.send_message(chat_id=chat_id,
                                        text=msg['msg_text'],
                                        entities=msg['entities'])
            else:
                # With keyboard '<< Закрыть'
                if len(msg['media_photo']) != 0 and msg['msg_caption'] is not None:
                    msg_response = bot.bot.send_photo(chat_id=chat_id,
                                    photo=download_file(bot, msg['media_photo'][0]),
                                    caption=msg['msg_caption'],
                                    caption_entities=msg['msg_caption_entities'],
                                    reply_markup=reply_markup)
                elif len(msg['media_photo']) != 0:
                    msg_response = bot.bot.send_photo(chat_id=chat_id,
                                    photo=download_file(bot, msg['media_photo'][0]),
                                    reply_markup=reply_markup)
                elif len(msg['media_video']) != 0 and msg['msg_caption'] is not None:
                    msg_response = bot.bot.send_video(chat_id=chat_id,
                                        video=download_file(bot, msg['media_video'][0]),
                                        caption=msg['msg_caption'],
                                        caption_entities=msg['msg_caption_entities'],
                                        reply_markup=reply_markup)
                elif len(msg['media_video']) != 0:
                    msg_response = bot.bot.send_video(chat_id=chat_id,
                                        video=download_file(bot, msg['media_video'][0]),
                                        reply_markup=reply_markup)
                else:
                    msg_response = bot.bot.send_message(chat_id=chat_id,
                                        text=msg['msg_text'],
                                        reply_markup=reply_markup,
                                        entities=msg['entities'])
        else:
            # Many photo/video send (media-group)
            media_photo_arr = [InputMediaPhoto(download_file(bot, one)) for one in msg['media_photo']]
            media_video_arr = [InputMediaVideo(download_file(bot, one)) for one in msg['media_video']]
            media_arr = media_photo_arr + media_video_arr
            media_arr[-1].caption = msg['msg_caption']
            media_arr[-1].caption_entities = msg['msg_caption_entities']
            msg_response = bot.bot.send_media_group(chat_id, media_arr)
        return msg_response
    except Exception as ex:
        pass
        

def post_loop(bot):

    print('[LOG] post_loop - started')

    while True:
        time.sleep(1)
        for msg in bot.later_msgs:

            if msg is None:
                bot.later_msgs.pop(bot.later_msgs.index(None))
                continue
            if msg['endpoint_date'] is not None and datetime.datetime.now() >= msg['endpoint_date']:
                continue
            
            today = datetime.datetime.now()
            if 'time_week_days' in msg:
                for wd_key in msg['time_week_days']:
                    if today.weekday() == wd_key and msg['time_week_days'][wd_key] == [today.hour, today.minute, today.second]:
                        # Time to send a message
                        try:
                            for chat_id in msg['chat_ids']:
                                msg_response = send_msg(bot, chat_id, msg)
                                if msg['is_pinned']:
                                    bot.bot.pin_chat_message(chat_id=chat_id,
                                                            message_id=msg_response.id)

                                # Chat-sender info (for bot2)
                                user = bot.find_user(msg['user_id'])
                                if chat_id not in user.chats_info:
                                    user.chats_info[chat_id] = [datetime.datetime.today()]
                                else:
                                    user.chats_info[chat_id].append(datetime.datetime.today())
                        except:
                            continue

            elif 'time_pub' in msg and today.weekday() in msg['week_days'] and msg['time_pub'] == [today.hour, today.minute, today.second]:
                
                # Time to send a message
                try:
                    for chat_id in msg['chat_ids']:
                        send_msg(bot, chat_id, msg)

                        # Chat-sender info (for bot2)
                        user = bot.find_user(msg['user_id'])
                        if chat_id not in user.chats_info:
                            user.chats_info[chat_id] = [datetime.datetime.today()]
                        else:
                            user.chats_info[chat_id].append(datetime.datetime.today())
                except:
                    continue

                # Pop sended-message from the 'later-list'
                # user.later_msgs.pop(user.later_msgs.index(msg))  
    

def download_file(bot, file_id):
    try:
        file_info = bot.bot.get_file(file_id)
        downloaded_file = bot.bot.download_file(file_info.file_path)
        return downloaded_file
    except:
        return None

# -------------------------------------------------------------------------------------------------


class User:
    def __init__(self, id, username=None,
                 is_logged=False, new_msg=None,
                 chat_ids_sender=list(),
                 chats_info=dict()):
        self.id = id
        self.username = username
        self.is_logged = is_logged
        self.new_msg = new_msg
        self.chat_ids_sender = chat_ids_sender
        self.chats_info = chats_info


class Bot:
    def __init__(self):
        self.bot = TeleBot(token=config.ACCESS_TOKEN)
        self.bot_password = '1234'
        self.chat_ids = [
            -1001690528285,
            -1001729568029,
            -1001661624582,
            -1001675440181,
            -1001794821899,
            -1001535125943,
            -1001265812935,
            -1001684221934,
            -1001753550558,
            -1001749819815,
            -1001280240711,
            -1001294371775,
            -1001234734402,
            -1001233106535,
            -1001511247081,
            -1001799532461,
            -1001690428264,
            -1001343222085,
            -1001587935512,
            -1001545794784,
            -1001666703485,
            -1001260420980,
            -1001170604218,
            -1001733716228,
            -1001624258588,
            -1001615241127,
            -1001676806834,
            -1001386773648,
            -1001677908658,
            -1001585234365,
            -1001708107827,
            -1001366485841,
            -1001765081234,
            -1001794681500,
            -1001927612030
        ]
        self.chat_titles = list()
        # self.test_channel_id = -1001927612030 # -1001913232751
        self.users = list()
        self.later_msgs = list()


    def find_user(self, id):
        for user in self.users:
            if str(user.id) == str(id):
                return user
        return None


    def find_msg(self, msg_start_time):
        for msg in self.later_msgs:
            if str(msg['start_time']) == str(msg_start_time):
                return msg
        return None
 

    def start(self):

        print('[LOG] Bot - started')
        self.chat_titles = []
        accept_ids = []
        for chat_id in self.chat_ids:
            try:
                chat_id = int(chat_id)
                self.chat_titles.append(self.bot.get_chat(chat_id).title)
                accept_ids.append(chat_id)
            except:
                continue
        self.chat_ids = [id for id in accept_ids]
        
        @self.bot.message_handler(commands=['start'])
        def start_msg(message):
            if message.chat.type != 'private':
                return
            
            self.bot.clear_step_handler_by_chat_id(message.chat.id)

            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if cur_user is None:
                cur_user = User(message.chat.id, message.from_user.username)
                self.users.append(cur_user)
            
            if not cur_user.is_logged:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Введите пароль:',
                                      reply_markup=keyboard.none())
                self.bot.register_next_step_handler(msg, log_in)
                return
            self.bot.send_message(chat_id=message.chat.id,
                                  text='== Главное меню ==',
                                  reply_markup=keyboard.menu())
        

        @self.bot.message_handler(content_types=['text'])
        def message_handle(message):
            if message.chat.type != 'private':
                return

            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if cur_user is None:
                cur_user = User(message.chat.id, message.from_user.username)
                self.users.append(cur_user)
            
            if not cur_user.is_logged:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Введите пароль:',
                                      reply_markup=keyboard.none())
                self.bot.register_next_step_handler(msg, log_in)
                return

            if message.text == 'Начать рассылку':
                cur_user.new_msg = None

                # Chat titles - check
                for chat_id in self.chat_ids:
                    try:
                        chat_title = self.bot.get_chat(chat_id).title
                        if chat_title not in self.chat_titles:
                            self.chat_titles.append(chat_title)
                    except:
                        continue
                
                self.bot.send_message(chat_id=message.chat.id,
                                      text='Выберете каналы для рассылки:',
                                      reply_markup=keyboard.chat_choose(self.chat_ids, 
                                                                             [(int(id) in cur_user.chat_ids_sender or str(id) in cur_user.chat_ids_sender) for id in self.chat_ids], 
                                                                             self.chat_titles))
            elif message.text == 'Запланированные публикации':

                while None in self.later_msgs:
                    self.later_msgs.pop(self.later_msgs.index(None))
                
                used_msgs = list()
                later_msgs = list()
                for msg in self.later_msgs:
                    if msg['start_time'] not in used_msgs:
                        used_msgs.append(msg['start_time'])
                        later_msgs.append(msg)
                self.later_msgs = [one for one in later_msgs]
                
                if len(self.later_msgs) == 0:
                    self.bot.send_message(chat_id=message.chat.id,
                                        text='Запланированные публикации отсутствуют!',
                                        reply_markup=keyboard.menu())
                else:
                    text = ''
                    week_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                    print(self.later_msgs)
                    for msg_i in range(len(self.later_msgs)):
                            
                        # Count of the letters in the post
                        if self.later_msgs[msg_i]['msg_caption'] is not None:
                            text_cnt = len(self.later_msgs[msg_i]['msg_caption'])
                        elif self.later_msgs[msg_i]['msg_text'] is not None:
                            text_cnt = len(self.later_msgs[msg_i]['msg_text'])
                        else:
                            text_cnt = 0
                    
                        if 'time_week_days' in self.later_msgs[msg_i]:
                            time_week_str = list()
                            for wk_day in self.later_msgs[msg_i]['time_week_days']:
                                hour, minute, second = self.later_msgs[msg_i]['time_week_days'][wk_day]
                                if len(str(minute)) < 2:
                                    minute = '0' + str(minute)
                                if len(str(hour)) < 2:
                                    hour = '0' + str(hour)
                                time_week_str.append(f'{week_days[int(wk_day)]} {hour}:{minute}')
                            time_week_str = ', '.join(time_week_str)
                            text += f'{msg_i + 1}) {self.later_msgs[msg_i]["post_name"][:30]}...\nДата: {time_week_str}\nКол-во символов: {text_cnt}\n\n'
                        else:
                            hour, minute, second = self.later_msgs[msg_i]['time_pub']
                            if len(str(minute)) < 2:
                                minute = '0' + str(minute)
                            if len(str(hour)) < 2:
                                hour = '0' + str(hour)
                            week_days_str = ", ".join([week_days[int(wk_day)] for wk_day in self.later_msgs[msg_i]["week_days"]])
                            text += f'{msg_i + 1}) {self.later_msgs[msg_i]["post_name"][:30]}...\nДата: {week_days_str} {hour}:{minute}\nКол-во символов: {text_cnt}\n\n'
                        # if self.later_msgs[msg_i]['msg_caption'] is not None:
                        #     text += f'{msg_i + 1}) {self.later_msgs[msg_i]["msg_caption"][:30]}...\n'
                        # elif self.later_msgs[msg_i]['msg_text'] is not None:
                        #     text += f'{msg_i + 1}) {self.later_msgs[msg_i]["msg_text"][:30]}...\n'
                    print(1)
                    self.bot.send_message(chat_id=message.chat.id,
                                          text=f'Запланированне публикации:\n\n{text}',
                                          reply_markup=keyboard.later_msgs_list(self.later_msgs))
            elif message.text == 'Настройки':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='== Настройки ==',
                                      reply_markup=keyboard.settings())
                self.bot.register_next_step_handler(msg, settings_menu)
            else:
                self.bot.send_message(chat_id=message.chat.id,
                                      text='Неизвестная команда!',
                                      reply_markup=keyboard.menu())
        

        @self.bot.message_handler(content_types=['photo'])
        def photo_handle(message):
            if message.chat.type != 'private':
                return
            
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if cur_user.new_msg is None:
                cur_user.new_msg = {
                    'user_id': cur_user.id,
                    'start_time': time.time(),
                    'group_id': message.media_group_id,
                    'media_photo': list(),
                    'media_video': list(),
                    'msg_caption': message.caption,
                    'msg_caption_entities': message.caption_entities,
                    'msg_text': message.text,
                    'chat_ids': cur_user.chat_ids_sender,
                    'entities': message.entities,
                    'endpoint_date': None,
                    'is_pinned': False,
                }
            elif 'msg_caption' not in cur_user.new_msg:
                cur_user.new_msg['msg_caption'] = message.caption
            elif 'msg_caption_entities' not in cur_user.new_msg:
                cur_user.new_msg['msg_caption_entities'] = message.caption_entities
            
            cur_user.new_msg['media_photo'].append(message.photo[-1].file_id)
        

        @self.bot.message_handler(content_types=['video'])
        def video_handle(message):
            if message.chat.type != 'private':
                return
            
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if cur_user.new_msg is None:
                cur_user.new_msg = {
                    'user_id': cur_user.id,
                    'start_time': time.time(),
                    'group_id': message.media_group_id,
                    'media_photo': list(),
                    'media_video': list(),
                    'msg_caption': message.caption,
                    'msg_caption_entities': message.caption_entities,
                    'msg_text': message.text,
                    'chat_ids': cur_user.chat_ids_sender,
                    'entities': message.entities,
                    'endpoint_date': None,
                    'is_pinned': False,
                }
            elif 'msg_caption' not in cur_user.new_msg:
                cur_user.new_msg['msg_caption'] = message.caption
            elif 'msg_caption_entities' not in cur_user.new_msg:
                cur_user.new_msg['msg_caption_entities'] = message.caption_entities
            
            cur_user.new_msg['media_video'].append(message.video.file_id)


        @self.bot.callback_query_handler(func=lambda x: True)
        def callback_handle(call):
            cur_user: User
            cur_user = self.find_user(call.message.chat.id)
            
            try:
                if len(call.data.split(':')) == 2:
                    prefix, data = call.data.split(':')
                elif len(call.data.split(':')) == 3:
                    prefix, data, add_data = call.data.split(':')
            except:
                self.bot.answer_callback_query(call.id)
                return
            
            if prefix == 'del_msg':
                self.bot.delete_message(chat_id=call.message.chat.id,
                                        message_id=call.message.id)
                self.bot.answer_callback_query(call.id)
            elif prefix == 'del':
                del_id = self.chat_ids.index(int(data))
                self.chat_ids.pop(del_id)
                self.chat_titles.pop(del_id)

                self.bot.answer_callback_query(call.id, 'Чат успешно удален!')
                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                           message_id=call.message.id,
                                           reply_markup=keyboard.groups_ids_del(self.chat_ids, self.chat_titles))
            elif prefix == 'choose':

                if data == 'done':
                    msg = self.bot.send_message(chat_id=call.message.chat.id,
                                          text='Пришлите сообщение для рассылки:',
                                          reply_markup=keyboard.back())
                    self.bot.register_next_step_handler(msg, sender_start)
                    return
                
                if data == 'all':
                    if len(cur_user.chat_ids_sender) != len(self.chat_ids):
                        cur_user.chat_ids_sender = [id for id in self.chat_ids]
                    else:
                        cur_user.chat_ids_sender = []
                else:
                    if int(data) in cur_user.chat_ids_sender:
                        cur_user.chat_ids_sender.pop(cur_user.chat_ids_sender.index(int(data)))
                    else:
                        cur_user.chat_ids_sender.append(int(data))

                # Chat titles - check
                for chat_id in self.chat_ids:
                    try:
                        chat_title = self.bot.get_chat(chat_id).title
                        if chat_title not in self.chat_titles:
                            self.chat_titles.append(chat_title)
                    except:
                        continue
                
                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                           message_id=call.message.id,
                                           reply_markup=keyboard.chat_choose(self.chat_ids, 
                                                                             [(int(id) in cur_user.chat_ids_sender or str(id) in cur_user.chat_ids_sender) for id in self.chat_ids], 
                                                                             self.chat_titles))
            elif prefix == 'later_msg_edit':
                msg_to_edit = self.find_msg(data)
                msg = self.bot.send_message(chat_id=call.message.chat.id,
                                      text='== Изменение объявления ==\n\nВыберите, что Вы хотите изменить:',
                                      reply_markup=keyboard.later_msg_edit_choose())
                self.bot.register_next_step_handler(msg, later_msg_edit_choose, msg_to_edit)
            elif prefix == 'later_msg_del':
                msg_to_del = self.find_msg(data)
                self.later_msgs.pop(self.later_msgs.index(msg_to_del))
                if len(self.later_msgs) == 0:
                    self.bot.edit_message_text(chat_id=call.message.chat.id,
                                                message_id=call.message.id,
                                                text='Запланированные публикации отсутствуют!')
                else:
                    text = ''
                    for msg_i in range(len(self.later_msgs)):
                        if self.later_msgs[msg_i]['msg_caption'] is not None:
                            text += f'{msg_i + 1}) {self.later_msgs[msg_i]["msg_caption"][:30]}...\n'
                        elif self.later_msgs[msg_i]['msg_text'] is not None:
                            text += f'{msg_i + 1}) {self.later_msgs[msg_i]["msg_text"][:30]}...\n'
                    self.bot.edit_message_text(chat_id=call.message.chat.id,
                                                message_id=call.message.id,
                                                text=f'Запланированные публикации:\n\n{text}',
                                                reply_markup=keyboard.later_msgs_list(self.later_msgs))
            elif prefix == 'later_msg_get':
                msg = self.find_msg(data)
                send_msg(self, call.message.chat.id, msg, keyboard.inline_close())
            elif prefix == 'later_msg_pin':
                msg = self.find_msg(data)
                msg['is_pinned'] = not msg['is_pinned']
                if msg['is_pinned']:
                    self.bot.answer_callback_query(call.id, 'Закреп включен!')
                else:
                    self.bot.answer_callback_query(call.id, 'Закреп выключен!')
                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                   message_id=call.message.id,
                                                   reply_markup=keyboard.later_msgs_list(self.later_msgs))
            elif prefix == 'week_days_choose':
                if data == 'done':
                    if 'week_days' not in cur_user.new_msg or len(cur_user.new_msg['week_days']) == 0:
                        self.bot.answer_callback_query(call.id, 'Нужно выбрать хотя бы 1 день недели!')
                        return
                    
                    msg = self.bot.send_message(chat_id=call.message.chat.id,
                                          text='Введите время публикации (час:мин):',
                                          reply_markup=keyboard.back())
                    self.bot.register_next_step_handler(msg, msg_sender_later)
                    return
                elif data == 'all':
                    if 'week_days' not in cur_user.new_msg or len(cur_user.new_msg['week_days']) == 0:
                        cur_user.new_msg['week_days'] = [i for i in range(7)]
                    else:
                        cur_user.new_msg['week_days'] = list()
                else:
                    if 'week_days' not in cur_user.new_msg  or len(cur_user.new_msg['week_days']) == 0:
                        cur_user.new_msg['week_days'] = [int(data)]
                    elif int(data) in cur_user.new_msg['week_days']:
                        cur_user.new_msg['week_days'].pop(cur_user.new_msg['week_days'].index(int(data)))
                    else:
                        cur_user.new_msg['week_days'].append(int(data))

                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                message_id=call.message.id,
                                                reply_markup=keyboard.week_days_choose(cur_user.new_msg['week_days']))
            elif prefix == 'edit_week_days_choose':
                msg_to_edit = self.find_msg(add_data)

                if data == 'done':
                    msg = self.bot.send_message(chat_id=call.message.chat.id,
                                          text='Введите время публикации (час:мин):',
                                          reply_markup=keyboard.back())
                    self.bot.register_next_step_handler(msg, msg_sender_later, msg_to_edit)
                    return
                elif data == 'all':
                    if 'week_days' not in msg_to_edit or len(msg_to_edit['week_days']) == 0:
                        msg_to_edit['week_days'] = [i for i in range(7)]
                    else:
                        msg_to_edit['week_days'] = list()
                else:
                    if 'week_days' not in msg_to_edit  or len(msg_to_edit['week_days']) == 0:
                        msg_to_edit['week_days'] = [int(data)]
                    elif int(data) in msg_to_edit['week_days']:
                        msg_to_edit['week_days'].pop(msg_to_edit['week_days'].index(int(data)))
                    else:
                        msg_to_edit['week_days'].append(int(data))

                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                message_id=call.message.id,
                                                reply_markup=keyboard.edit_week_days_choose(msg_to_edit['start_time'], 
                                                                                            msg_to_edit['week_days']))
            elif prefix == 'edit_choose':
                msg_to_edit = self.find_msg(add_data)

                if data == 'done':
                    msg = self.bot.send_message(chat_id=call.message.chat.id,
                                          text='Группы для публикации изменены!',
                                          reply_markup=keyboard.menu())
                    return
                
                if data == 'all':
                    if len(msg_to_edit['chat_ids']) != len(self.chat_ids):
                        msg_to_edit['chat_ids'] = [id for id in self.chat_ids]
                    else:
                        msg_to_edit['chat_ids'] = []
                else:
                    if int(data) in msg_to_edit['chat_ids']:
                        msg_to_edit['chat_ids'].pop(msg_to_edit['chat_ids'].index(int(data)))
                    else:
                        msg_to_edit['chat_ids'].append(int(data))

                # Chat titles - check
                for chat_id in self.chat_ids:
                    try:
                        chat_title = self.bot.get_chat(chat_id).title
                        if chat_title not in self.chat_titles:
                            self.chat_titles.append(chat_title)
                    except:
                        continue
                
                self.bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                           message_id=call.message.id,
                                           reply_markup=keyboard.edit_chat_choose(add_data,
                                                                                  self.chat_ids, 
                                                                             [(int(id) in msg_to_edit['chat_ids'] or str(id) in msg_to_edit['chat_ids']) for id in self.chat_ids], 
                                                                             self.chat_titles))
            elif prefix == 'time_week_days_choose':
                if data in ['continue', 'done']:
                    if data == 'continue':
                        cur_user.new_msg.pop('time_week_days')
                    msg = self.bot.send_message(chat_id=call.message.chat.id,
                                                text='Введите конечную дату публикации (дд.мм.гггг):',
                                                reply_markup=keyboard.back_continue())
                    self.bot.register_next_step_handler(msg, msg_sender_endpoint)
                else:
                    msg = self.bot.send_message(chat_id=call.message.chat.id,
                                          text='Введите время публикации (час:мин):',
                                          reply_markup=keyboard.back())
                    self.bot.register_next_step_handler(msg, msg_sender_later, time_wd_key=data)
            elif prefix == 'edit_time_week_days_choose':
                edit_msg = self.find_msg(add_data)
                if data in ['continue', 'done']:
                    if data == 'continue':
                        edit_msg.pop('time_week_days')
                    self.bot.send_message(chat_id=call.message.chat.id,
                                            text='Публикация изменена!',
                                            reply_markup=keyboard.menu())
                else:
                    msg = self.bot.send_message(chat_id=call.message.chat.id,
                                          text='Введите время публикации (час:мин):',
                                          reply_markup=keyboard.back())
                    self.bot.register_next_step_handler(msg, msg_sender_later, edit_msg=edit_msg, time_wd_key=data)


        def log_in(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == self.bot_password:
                cur_user.is_logged = True
                self.bot.send_message(chat_id=message.chat.id,
                                      text='Пароль введен успешно!\n== Главное меню ==',
                                      reply_markup=keyboard.menu())
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Некорректный пароль!\nВведите пароль:',
                                      reply_markup=keyboard.none())
                self.bot.register_next_step_handler(msg, log_in)
                

# ---- Settings -----------------------------------------------------------------------------------

        def settings_menu(message):
            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard.menu())
            elif message.text == 'Изменить пароль бота':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text=f'Прошлый пароль: <b>{self.bot_password}</b>\nВведите новый:',
                                      parse_mode='html',
                                      reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, edit_bot_password)
            elif message.text == 'Добавить группу/канал':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Введите ID новой группы/канала:',
                                            reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, add_new_group)
            elif message.text == 'Удалить группу/канал':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Выберете ID группы/канала, который хотиете удалить:',
                                            reply_markup=keyboard.groups_ids_del(self.chat_ids, self.chat_titles))
                self.bot.register_next_step_handler(msg, settings_menu)
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Неизвестная команда!',
                                            reply_markup=keyboard.settings())
                self.bot.register_next_step_handler(msg, settings_menu)
        

        def edit_bot_password(message):
            if message.text == '<< Назад':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='== Настройки ==',
                                      reply_markup=keyboard.settings())
            else:
                self.bot_password = message.text
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text=f'Пароль успешно изменен!\nНовый пароль: <b>{self.bot_password}</b>',
                                      reply_markup=keyboard.settings(),
                                      parse_mode='html')
            self.bot.register_next_step_handler(msg, settings_menu)
        

        def add_new_group(message):
            if message.text == '<< Назад':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='== Настройки ==',
                                      reply_markup=keyboard.settings())
                self.bot.register_next_step_handler(msg, settings_menu)
            elif not is_num(message.text):
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='ID группы должен быть числом!\nВведите ID новой группы/канала:',
                                      reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, add_new_group)
            elif int(message.text) in self.chat_ids:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Это группа уже добавлена!\nВведите ID новой группы/канала:',
                                            reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, add_new_group)
            else:
                try:
                    self.chat_ids.append(int(message.text))
                    try:
                        self.chat_titles.append(self.bot.get_chat(int(message.text)).title)
                    except:
                        self.chat_titles.append('None')
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                          text='Новая группа/канал успешно добавлена!',
                                          reply_markup=keyboard.settings())
                    self.bot.register_next_step_handler(msg, settings_menu)
                except:
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                          text='Некорректный ID группы/канала!\nВведите ID новой группы/канала:',
                                          reply_markup=keyboard.back())
                    self.bot.register_next_step_handler(msg, add_new_group)
        
# -------------------------------------------------------------------------------------------------

# ---- Sender -------------------------------------------------------------------------------------

        def sender_start(message):
            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard.menu())
                return
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Выберите тип рассылки:',
                                      reply_markup=keyboard.choose_sender_type())
                self.bot.register_next_step_handler(msg, choose_sender_type, message)
        

        def choose_sender_type(message, msg_sender):
            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard.menu())
                return
            elif message.text == 'Запланировать публикацию':

                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Введите название публикации (до 4-х слов):',
                                      reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, sheduled_post_name, msg_sender)

            elif message.text == 'Разместить сейчас':
                
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Запинить пост?',
                                            reply_markup=keyboard.yes_no())
                self.bot.register_next_step_handler(msg, is_pinned_post, msg_sender)
                
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Неизвестная команда!\nВыберите тип рассылки:',
                                      reply_markup=keyboard.choose_sender_type())
                self.bot.register_next_step_handler(msg, choose_sender_type, message)


        def is_pinned_post(message, msg_sender):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard.menu())
                return

            if message.text == 'Да':
                is_pinned = True
            elif message.text == 'Нет':
                is_pinned = False
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Запинить пост?',
                                            reply_markup=keyboard.yes_no())
                self.bot.register_next_step_handler(msg, is_pinned_post, msg_sender)
                return
            
            if msg_sender.media_group_id is None:
                # No group message type (one photo)
                if msg_sender.photo is not None and msg_sender.caption is not None:
                    # Photo + Caption
                    downloaded_photo = download_file(self, msg_sender.photo[-1].file_id)
                    for chat_id in cur_user.chat_ids_sender:
                        msg_response = self.bot.send_photo(chat_id=chat_id,
                                            photo=downloaded_photo,
                                            caption=msg_sender.caption,
                                            caption_entities=msg_sender.caption_entities)
                        
                elif msg_sender.photo is not None:
                    # Photo
                    downloaded_photo = download_file(self, msg_sender.photo[-1].file_id)
                    for chat_id in cur_user.chat_ids_sender:
                        msg_response = self.bot.send_photo(chat_id=chat_id,
                                            photo=downloaded_photo)
                        
                elif msg_sender.video is not None and msg_sender.caption is not None:
                    # Video + Caption
                    downloaded_video = download_file(self, msg_sender.video.file_id)
                    for chat_id in cur_user.chat_ids_sender:
                        msg_response = self.bot.send_video(chat_id=chat_id,
                                            video=downloaded_video,
                                            caption=msg_sender.caption,
                                            caption_entities=msg_sender.caption_entities)
                    
                elif msg_sender.video is not None:
                    # Video
                    downloaded_video = download_file(self, msg_sender.video.file_id)
                    for chat_id in cur_user.chat_ids_sender:
                        msg_response = self.bot.send_video(chat_id=chat_id,
                                            video=downloaded_video)
                        
                else:
                    # Only text
                    for chat_id in cur_user.chat_ids_sender:
                        msg_response = self.bot.send_message(chat_id=chat_id,
                                            text=msg_sender.text,
                                            entities=msg_sender.entities)
                        
                self.bot.send_message(chat_id=msg_sender.chat.id,
                                text='Рассылка успешно завершена!',
                                reply_markup=keyboard.menu())

                for chat_id in cur_user.chat_ids_sender:
                    if is_pinned:
                        self.bot.pin_chat_message(chat_id=chat_id,
                                                message_id=msg_response.id)

                # Chat-sender info (for bot2)
                for chat_id in cur_user.chat_ids_sender:
                    if chat_id not in cur_user.chats_info:
                        cur_user.chats_info[chat_id] = [datetime.datetime.today()]
                    else:
                        cur_user.chats_info[chat_id].append(datetime.datetime.today())
            else:
                # Group message type (many photos)
                if msg_sender.photo is not None:

                    if cur_user.new_msg is None:
                        cur_user.new_msg = {
                            'user_id': cur_user.id,
                            'start_time': time.time(),
                            'group_id': msg_sender.media_group_id,
                            'media_photo': [msg_sender.photo[-1].file_id],
                            'media_video': list(),
                            'msg_caption': msg_sender.caption,
                            'msg_caption_entities': msg_sender.caption_entities,
                            'msg_text': message.text,
                            'chat_ids': cur_user.chat_ids_sender,
                            'entities': msg_sender.entities,
                            'endpoint_date': None,
                            'is_pinned': False,
                        }
                    elif msg_sender.photo[-1].file_id not in cur_user.new_msg['media_photo']:
                        cur_user.new_msg['media_photo'].append(msg_sender.photo[-1].file_id)
                        cur_user.new_msg['msg_caption'] = msg_sender.caption
                        cur_user.new_msg['msg_caption_entities'] = msg_sender.caption_entities

                elif msg_sender.video is not None:

                    if cur_user.new_msg is None:
                        cur_user.new_msg = {
                            'user_id': cur_user.id,
                            'start_time': time.time(),
                            'group_id': msg_sender.media_group_id,
                            'media_photo': list(),
                            'media_video': [msg_sender.video.file_id],
                            'msg_caption': msg_sender.caption,
                            'msg_caption_entities': msg_sender.caption_entities,
                            'msg_text': message.text,
                            'chat_ids': cur_user.chat_ids_sender,
                            'entities': msg_sender.entities,
                            'endpoint_date': None,
                            'is_pinned': False,
                        }
                    elif msg_sender.video.file_id not in cur_user.new_msg['media_video']:
                        cur_user.new_msg['media_video'].append(msg_sender.video.file_id)
                        cur_user.new_msg['msg_caption'] = msg_sender.caption
                        cur_user.new_msg['msg_caption_entities'] = msg_sender.caption_entities

                # Pin msg
                cur_user.new_msg['is_pinned'] = is_pinned

                threading.Thread(target=wait_n_seconds, args=(self, self.find_user(msg_sender.chat.id), 5,)).start()
            


        def sheduled_post_name(message, msg_sender):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard.menu())
                return
            elif len(message.text.split()) > 4:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Максимальное кол-во слов: 4!\nВведите название публикации (до 4-х слов):',
                                      reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, sheduled_post_name, msg_sender)
                return

            if cur_user.new_msg is None:
                cur_user.new_msg = {
                    'user_id': cur_user.id,
                    'group_id': msg_sender.media_group_id,
                    'start_time': time.time(),
                    'media_photo': list(),
                    'media_video': list(),
                    'msg_caption': msg_sender.caption,
                    'msg_caption_entities': msg_sender.caption_entities,
                    'msg_text': msg_sender.text,
                    'chat_ids': cur_user.chat_ids_sender,
                    'entities': msg_sender.entities,
                    'endpoint_date': None,
                    'is_pinned': False,
                }
            
            cur_user.new_msg['post_name'] = message.text

            if msg_sender.media_group_id is None:
                # No group message type (one photo)
                if msg_sender.photo is not None:
                    cur_user.new_msg['media_photo'] = [msg_sender.photo[-1].file_id]
                elif msg_sender.video is not None:
                    cur_user.new_msg['media_video'] = [msg_sender.video.file_id]

            else:
                # Group message type (many photos)
                if msg_sender.photo is not None:

                    if msg_sender.photo[-1].file_id not in cur_user.new_msg['media_photo']:
                        cur_user.new_msg['media_photo'].append(msg_sender.photo[-1].file_id)
                        cur_user.new_msg['msg_caption'] = msg_sender.caption
                        cur_user.new_msg['msg_caption_entities'] = msg_sender.caption_entities

                elif msg_sender.video is not None:

                    if msg_sender.video.file_id not in cur_user.new_msg['media_video']:
                        cur_user.new_msg['media_video'].append(msg_sender.video.file_id)
                        cur_user.new_msg['msg_caption'] = msg_sender.caption
                        cur_user.new_msg['msg_caption_entities'] = msg_sender.caption_entities
                else:
                    cur_user.new_msg['entities'] = msg_sender.entities

                threading.Thread(target=wait_n_seconds_later, args=(self, self.find_user(msg_sender.chat.id), 5,)).start()
                
            self.bot.send_message(chat_id=message.chat.id,
                                    text='Выберите дни недели:',
                                    reply_markup=keyboard.week_days_choose(list()))


        def msg_sender_later(message, edit_msg=None, time_wd_key=None):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard.menu())
                return
            else:
                try:
                    if edit_msg:
                        cur_user.new_msg = edit_msg
                    hour, minute = [int(one) for one in message.text.split(':')]
                    if edit_msg is None:
                        print(cur_user.new_msg)
                        if cur_user.new_msg is None:
                            cur_user.new_msg = {}
                            cur_user.new_msg['week_days'] = []
                        else:
                            if 'week_days' in cur_user.new_msg:
                                cur_user.new_msg['week_days'] = list(set(cur_user.new_msg['week_days']))
                            else:
                                cur_user.new_msg['week_days'] = []
                        
                        # Add multiple choice of the time for week-days
                        if 'time_week_days' not in cur_user.new_msg:
                            cur_user.new_msg['time_week_days'] = dict()
                            for wd_i in cur_user.new_msg['week_days']:
                                cur_user.new_msg['time_week_days'][wd_i] = [hour, minute, 0]

                        if time_wd_key is None:
                            cur_user.new_msg['time_pub'] = [hour, minute, 0]
                        else:
                            cur_user.new_msg['time_week_days'][int(time_wd_key)] = [hour, minute, 0]
                        
                        msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Выберите дни недели, для которых хотите указать другое время публикации:',
                                            reply_markup=keyboard.later_msg_time_choose(cur_user.new_msg['time_week_days']))

                        # msg = self.bot.send_message(chat_id=message.chat.id,
                        #                             text='Введите конечную дату публикации (дд.мм.гггг):',
                        #                             reply_markup=keyboard.back_continue())
                        # self.bot.register_next_step_handler(msg, msg_sender_endpoint)
                    else:
                        print(edit_msg)
                        cur_user.new_msg['week_days'] = edit_msg['week_days']
                        edit_msg['week_days'] = list(set(edit_msg['week_days']))

                        if 'time_week_days' in edit_msg:
                            if time_wd_key is not None:
                                edit_msg['time_week_days'][int(time_wd_key)] = [hour, minute, 0]
                            else:
                                edit_msg['time_week_days'] = dict()
                                for wd_i in edit_msg['week_days']:
                                    edit_msg['time_week_days'][wd_i] = [hour, minute, 0]
                        else:
                            edit_msg['time_week_days'] = dict()
                            for wd_i in edit_msg['week_days']:
                                edit_msg['time_week_days'][wd_i] = [hour, minute, 0]
                        msg = self.bot.send_message(chat_id=message.chat.id,
                                                    text='Выберите дни недели, для которых хотите указать другое время публикации:',
                                                    reply_markup=keyboard.edit_later_msg_time_choose(
                                                        edit_msg['time_week_days'], edit_msg['start_time']))
                        # self.bot.send_message(chat_id=message.chat.id,
                        #                         text='Публикация изменена!',
                        #                         reply_markup=keyboard.menu())
                except Exception as ex:
                    print(ex)
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='Введите время публикации повторно (час:мин)',
                                      reply_markup=keyboard.back())
                    self.bot.register_next_step_handler(msg, msg_sender_later)
        

        def msg_sender_endpoint(message):
            cur_user: User
            cur_user = self.find_user(message.chat.id)

            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard.menu())
                return
            elif message.text != 'Пропустить':
                try:
                    day, month, year = list(map(int, message.text.split('.')))
                    cur_user.new_msg['endpoint_date'] = datetime.datetime(year, month, day)
                except:
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                                    text='Неккоректный ввод даты!\nВведите конечную дату публикации (дд.мм.гггг):',
                                                    reply_markup=keyboard.back_continue())
                    self.bot.register_next_step_handler(msg, msg_sender_endpoint)
                    return
                
            time.sleep(4)

            if self.find_msg(cur_user.new_msg['start_time']) is None:
                self.later_msgs.append(cur_user.new_msg)
            cur_user.new_msg = None

            self.bot.send_message(chat_id=message.chat.id,
                                    text='Публикация запланирована!',
                                    reply_markup=keyboard.menu())
                    

        def later_msg_edit_choose(message, msg_to_edit):
            if message.text == '<< Назад':
                self.bot.send_message(chat_id=message.chat.id,
                                      text='== Главное меню ==',
                                      reply_markup=keyboard.menu())
            elif message.text == 'Изменить название публикации':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='== Изменение объявления ==\n\nВведите новое название публикации:',
                                        reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, edit_name_later_msgs, msg_to_edit)
            elif message.text == 'Изменить текст публикации':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='== Изменение объявления ==\n\nПришлите новый текст публикации:',
                                        reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, edit_text_later_msgs, msg_to_edit)
            elif message.text == 'Изменить дату и время публикации':
                self.bot.send_message(chat_id=message.chat.id,
                                        text='== Изменение объявления ==\n\nВыберите дни недели:',
                                        reply_markup=keyboard.edit_week_days_choose(msg_to_edit['start_time'], 
                                                                                    msg_to_edit['week_days']))
            elif message.text == 'Изменить выбранные группы':
                self.bot.send_message(chat_id=message.chat.id,
                                        text='== Изменение объявления ==\n\nВыберите группы:',
                                        reply_markup=keyboard.edit_chat_choose(msg_to_edit['start_time'],
                                                                               self.chat_ids, 
                                                                             [(int(id) in msg_to_edit['chat_ids'] or str(id) in msg_to_edit['chat_ids']) for id in self.chat_ids], 
                                                                             self.chat_titles))
            elif message.text == 'Изменить конечную дату публикации':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                        text='== Изменение объявления ==\n\nВведите новую конечную дату публикации:',
                                        reply_markup=keyboard.back())
                self.bot.register_next_step_handler(msg, edit_endpoint_date, msg_to_edit)
            else:
                msg = self.bot.send_message(chat_id=message.chat.id,
                                            text='Неизвестная команда!\nВыберите, что Вы хотите изменить:',
                                            reply_markup=keyboard.later_msg_edit_choose())
                self.bot.register_next_step_handler(msg, later_msg_edit_choose, msg_to_edit)
        

        def edit_name_later_msgs(message, msg_to_edit):
            if message.text == '<< Назад':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='== Изменение объявления ==\n\nВыберите, что Вы хотите изменить:',
                                      reply_markup=keyboard.later_msg_edit_choose())
                self.bot.register_next_step_handler(msg, later_msg_edit_choose, msg_to_edit)
            else:
                msg_to_edit['post_name'] = message.text
                self.bot.send_message(chat_id=message.chat.id,
                                          text='Публикация успешно изменена!',
                                          reply_markup=keyboard.menu())


        def edit_text_later_msgs(message, msg_to_edit):
            if message.text == '<< Назад':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='== Изменение объявления ==\n\nВыберите, что Вы хотите изменить:',
                                      reply_markup=keyboard.later_msg_edit_choose())
                self.bot.register_next_step_handler(msg, later_msg_edit_choose, msg_to_edit)
            else:
                cur_user: User
                cur_user = self.find_user(message.chat.id)

                if cur_user.new_msg is None:
                    cur_user.new_msg = {
                        'user_id': cur_user.id,
                        'start_time': time.time(),
                        'group_id': message.media_group_id,
                        'media_photo': list(),
                        'media_video': list(),
                        'msg_caption': message.caption,
                        'msg_caption_entities': message.caption_entities,
                        'msg_text': message.text,
                        'chat_ids': msg_to_edit['chat_ids'],
                        'entities': message.entities,
                        'is_pinned': False,
                    }

                    for key in msg_to_edit:
                        if key not in cur_user.new_msg:
                            cur_user.new_msg[key] = msg_to_edit[key]

                if message.media_group_id is None:
                    # No group message type (one photo)
                    if message.photo is not None:
                        cur_user.new_msg['media_photo'] = [message.photo[-1].file_id]
                        cur_user.new_msg['msg_caption'] = message.caption
                        cur_user.new_msg['msg_caption_entities'] = message.caption_entities
                    elif message.video is not None:
                        cur_user.new_msg['media_video'] = [message.video.file_id]
                        cur_user.new_msg['msg_caption'] = message.caption
                        cur_user.new_msg['msg_caption_entities'] = message.caption_entities

                    self.later_msgs.pop(self.later_msgs.index(msg_to_edit))
                    self.later_msgs.append(cur_user.new_msg)

                    self.bot.send_message(chat_id=message.chat.id,
                                          text='Публикация успешно изменена!',
                                          reply_markup=keyboard.menu())
                else:
                    # Group message type (many photos)
                    if message.photo is not None:

                        if message.photo[-1].file_id not in cur_user.new_msg['media_photo']:
                            cur_user.new_msg['media_photo'].append(message.photo[-1].file_id)
                            cur_user.new_msg['msg_caption'] = message.caption
                            cur_user.new_msg['msg_caption_entities'] = message.caption_entities

                    elif message.video is not None:

                        if message.video.file_id not in cur_user.new_msg['media_video']:
                            cur_user.new_msg['media_video'].append(message.video.file_id)
                            cur_user.new_msg['msg_caption'] = message.caption
                            cur_user.new_msg['msg_caption_entities'] = message.caption_entities

                    threading.Thread(target=wait_n_seconds_later, args=(self, self.find_user(message.chat.id), 5, msg_to_edit,)).start()


        def edit_endpoint_date(message, edit_msg):
            if message.text == '<< Назад':
                msg = self.bot.send_message(chat_id=message.chat.id,
                                      text='== Изменение объявления ==\n\nВыберите, что Вы хотите изменить:',
                                      reply_markup=keyboard.later_msg_edit_choose())
                self.bot.register_next_step_handler(msg, later_msg_edit_choose, edit_msg)
            else:
                try:
                    day, month, year = list(map(int, message.text.split('.')))
                    edit_msg['endpoint_date'] = datetime.datetime(year, month, day)
                    print(edit_msg)
                    self.bot.send_message(chat_id=message.chat.id,
                                          text='Конечная дата успешно изменена!',
                                          reply_markup=keyboard.menu())
                except:
                    msg = self.bot.send_message(chat_id=message.chat.id,
                                                    text='Неккоректный ввод даты!\nВведите конечную дату публикации (дд.мм.гггг):',
                                                    reply_markup=keyboard.back_continue())
                    self.bot.register_next_step_handler(msg, edit_endpoint_date, edit_msg)
                    return

# -------------------------------------------------------------------------------------------------

        self.bot.infinity_polling()


def main():
    bot = Bot()
    add_bot = bot2.Bot2()

    # DB load
    load_from_db(bot, add_bot)

    # Main bot
    threading.Thread(target=bot.start).start()
    threading.Thread(target=post_loop, args=(bot,)).start()

    # Additional bot
    threading.Thread(target=add_bot.start, args=(bot,)).start()

    # DB save
    threading.Thread(target=save_loop, args=(bot, add_bot,)).start()


if __name__ == '__main__':
    main()
