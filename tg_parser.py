import configparser
import json
from telethon.sync import TelegramClient
# для корректного переноса времени сообщений в json
from datetime import datetime
# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest


all_messages = []

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")
# Присваиваем значения внутренним переменным
api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, api_id, api_hash)
client.start()


TG_CHANNELS = ['@nexta_live', '@meduzalive', '@first_political', '@moscowach', '@otsuka_bld', '@rian_ru', '@filth_pit', '@dvachannel', '@rhymesthrash', '@rand2ch', '@breakingmash', '@lifeyt']


class DateTimeEncoder(json.JSONEncoder):
    '''Класс для сериализации записи дат в JSON'''
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, bytes):
            return list(o)
        return json.JSONEncoder.default(self, o)


def save_to_json(data):
    with open('channel_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, cls=DateTimeEncoder)


async def dump_all_messages(channel):
    offset_msg = -1    # номер записи, с которой начинается считывание
    limit_msg = 10   # максимальное число записей, передаваемых за один раз
    total_messages = 0 # список всех сообщений
    total_count_limit = 100  # количество сообщений с текстом с одного канала
    channel_messages = []
    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            if message.message:
                msg = {'channel': channel, 'date': message.date, 'message': message.message}
                channel_messages.append(msg)
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(channel_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            global all_messages 
            all_messages += channel_messages
            channel_messages.clear()
            break


async def dump_channels():
    for index, channel in enumerate(TG_CHANNELS):
        print(f'№{index + 1 } из {len(TG_CHANNELS) + 1} - {channel}')
        await dump_all_messages(channel)
    save_to_json(all_messages)
