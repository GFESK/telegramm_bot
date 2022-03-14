from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import json
from tg_parser import dump_channels
from config import TOKEN
from search import similarity

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


def read_file():
    f = open('channel_messages.json', encoding='utf-8')
    data = json.load(f)
    return data


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("\nПожалуйста, в первую очередь сохраните каналы командой /save . Далее отправьте боту сообщение или новость, для которой хотите найти первоисточник")
    

@dp.message_handler(commands=['save'])
async def process_start_command(message: types.Message):
    await message.reply("\nНачинаю парсить каналы.")
    await dump_channels()
    await message.reply("\nДанные успешно загружены!\nТеперь можете отправить боту сообщение, и он попробует найти первоисточник!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Вбейте /start, и следуйте инструкциям!")


@dp.message_handler()
async def echo_message(message: types.Message):
    try:
        possible_text, channel, text_date = await similarity(message.text)
        await message.reply(f'Возможный первоисточник-канал: {channel}\nДата сообщения: {text_date}\nСообщение: {possible_text}')
    except Exception:
        await message.reply('Похожих сообщений не найдено!')
    


def start():
    executor.start_polling(dp)