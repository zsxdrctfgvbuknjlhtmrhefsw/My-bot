import random

from aiogram import types
from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError

from load_all import bot, dp, db


class DBCommands:
    pool: Connection = db
    ADD_NEW_USER_REFERRAL = "INSERT INTO users(chat_id, username, full_name, referral) " \
                            "VALUES ($1, $2, $3, $4) RETURNING id"
    ADD_NEW_USER = "INSERT INTO users(chat_id, username, full_name) VALUES ($1, $2, $3) RETURNING id"
    COUNT_USERS = "SELECT COUNT(*) FROM users"
    GET_ID = "SELECT id FROM users WHERE chat_id = $1"
    CHECK_REFERRALS = "SELECT chat_id FROM users WHERE referral=" \
                      "(SELECT id FROM users WHERE chat_id=$1)"
    CHECK_BALANCE = "SELECT balance FROM users WHERE chat_id = $1"
    ADD_MONEY = "UPDATE users SET balance=balance+$1 WHERE chat_id = $2"

    async def add_new_user(self, referral=None):
        user = types.User.get_current()

        chat_id = user.id
        username = user.username
        full_name = user.full_name
        args = chat_id, username, full_name

        if referral:
            args += (int(referral),)
            command = self.ADD_NEW_USER_REFERRAL
        else:
            command = self.ADD_NEW_USER

        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def count_users(self):
        record: Record = await self.pool.fetchval(self.COUNT_USERS)
        return record

    async def get_id(self):
        command = self.GET_ID
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)

    async def check_referrals(self):
        user_id = types.User.get_current().id
        command = self.CHECK_REFERRALS
        rows = await self.pool.fetch(command, user_id)
        return ", ".join([
            f"{num + 1}. " + (await bot.get_chat(user["chat_id"])).get_mention(as_html=True)
            for num, user in enumerate(rows)
        ])

    async def check_balance(self):
        command = self.CHECK_BALANCE
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)

    async def add_money(self, money):
        command = self.ADD_MONEY
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, money, user_id)


db = DBCommands()


@dp.message_handler(commands=["start"])
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    referral = message.get_args()
    id = await db.add_new_user(referral=referral)
    count_users = await db.count_users()

    text = ""
    if not id:
        id = await db.get_id()
    else:
        text += "Записал в базу! "

    bot_username = (await bot.me).username
    bot_link = f"https://t.me/{bot_username}?start={id}"
    balance = await db.check_balance()

    await message.reply(start_message, reply_markup=kb.markup3)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(help_message, reply_markup=kb.markup3)


@dp.message_handler(content_types=['text'])
async def get_text_messages(message):
    if message.text == "Платные опросы":
        keyboard = types.InlineKeyboardMarkup()
        url_button1 = types.InlineKeyboardButton(text="Анкетка.ру", url="https://www.anketka.ru/referral/6869423")
        url_button2 = types.InlineKeyboardButton(text="You think", url="https://youthink.io/?source=e3L1m9__kk")
        url_button3 = types.InlineKeyboardButton(text="Мое мнение", url="https://www.moemnenie.ru/f/11156912")
        keyboard.add(url_button1).add(url_button2).add(url_button3)
        await message.reply(opros_message, reply_markup=keyboard)
    elif message.text == "Для мобильного телефона":
        keyboard_1 = types.InlineKeyboardMarkup()
        url_button4 = types.InlineKeyboardButton(text="Apperwall", url="https://apperwall.com/?p=2DdEhKcy")
        url_button5 = types.InlineKeyboardButton(text="Advertapp на Android", url="http://go.advertapp.net/4a8qq5")
        url_button6 = types.InlineKeyboardButton(text="PayForInstall на Android", url="https://play.google.com/store/apps/details?id=melchindmitry.oncreate.pfi")
        url_button7 = types.InlineKeyboardButton(text="PayForInstall на iOS", url="https://apps.apple.com/ru/app/pfi/id1450915982")
        keyboard_1.add(url_button4).add(url_button5).add(url_button6).add(url_button7)
        await message.reply(game_message, reply_markup=keyboard_1)
    elif message.text == "Фриланс":
        keyboard_2 = types.InlineKeyboardMarkup()
        url_button8 = types.InlineKeyboardButton(text="Advego", url="https://advego.com/8XgEQdtkrk")
        url_button9 = types.InlineKeyboardButton(text="Work-zilla", url="https://work-zilla.com/?ref=1436000")
        url_button10 = types.InlineKeyboardButton(text="FL.ru", url="https://www.fl.ru/projects/?ref=158503")
        keyboard_2.add(url_button8).add(url_button9).add(url_button10)
        await message.reply(freelance_message, reply_markup=keyboard_2)
    else:
        await message.reply('Я тебя не понимаю. Напиши /help.')
