# импорты
from datetime import datetime, timedelta
import asyncio
import re
import logging
import random
import time
from flyerapi import Flyer

# pyro
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters, idle, errors
from pyrogram.enums import ChatMemberStatus, ParseMode, ChatType, ChatAction, MessageMediaType
from pyrogram.errors import UserIsBlocked, InputUserDeactivated, UserNotParticipant, UsernameInvalid, FloodWait, \
    UserDeactivated, UserBlocked, ChatAdminRequired, UserAdminInvalid, MessageDeleteForbidden
from pyrogram.raw.functions.channels import CreateForumTopic, EditForumTopic
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent, InputMediaPhoto, InputMediaVideo,
                            InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ChatPermissions,
                            ChatPrivileges)

# переносим все конфиги, включая токен, запрещенные слова и картинки
from config import DIMA, themes, API_TOKEN, mm_pictures, no_info_pictures, scam_pictures, staff_pictures, \
    high_chances_pictures, good_morning_pictures, good_morning_advices, good_night_pictures, good_night_advices, \
    bad_stickers, trusted_pictures, channel, report_group, TOKEN, numberEmojies, lol

from functions import dotdict, get_date, get_country, get_country_emojie

# клавиатуры
from keyboards import MAIN_KB, AS_REPORT_KB, CHANNEL_KB, DEFAULT_KB, HIDE_KB, WHAT_TO_DO_KB, COUNTRIES_1
from sqlite3_functions import sql_edit, sql_select, sqlite_start_commands, connection, scam_list, \
    support_symbols

the_most_recent_search = '<i>Пользователь скрыт</i>'
commands_use = {}
banned = []
adm_limits = {}
report_in_progress = []

commands = {
    'check': 0, 'start': 0, 'stats': 0, 'me': 0, 'report': 0, 'help': 0, 'admins': 0, 'mms': 0,
    'scamwarn': 0, 'shown': 0, 'hidden': 0, 'banned': 0, 'changed': 0,
}
commands = dotdict(commands)

hints = (
    'Вы можете <a href=https://t.me/AntiscamDatabaseBot?startgroup=new>добавить бота в свой чат</a>,'
    'чтобы он предупреждал участников о скаммерах',
    'Слить скаммера можно в <a href=tg://resolve?domain=GasdReport>нашем чате жалоб</a>',
    'Следите за новостями на <a href=https://t.me/AntiScamRoblox>нашем канале</a>',
    'Пропадают кнопки в боте? Пропишите /start',
    'Ставьте <code>△</code> в свой ник, если вы поддерживаете борьбу со скамом',
    'Заходите играть в <a href=https://t.me/YozhChat>чате Ёжиков</a>',
    'Устанавливайте <a href=https://t.me/addemoji/AntiscamBaza>наши эмодзи</a>',
    'У нас есть <a href=https://t.me/GasdChat>чат для общения</a>',
)

logging.basicConfig(level=logging.INFO)

for i in sqlite_start_commands:
    sql_edit(i, ())
    
userbot = Client("papaburger", api_id=твой апи айди, api_hash='твой апи хеш')

flyer = Flyer('FL-nQnelI-FowwzW-QgoiEH-vfnoBL')


apps = [
    Client("gasd_bot", api_id=твой апи айди, api_hash='твой апи хеш', bot_token=API_TOKEN),

]

for app in apps:
    
    app.sleep_threshold = 2
    app.parse_mode = ParseMode.HTML
    
    async def bot_id():
        return (await app.get_me()).id
    
    async def get_user_id(userid):
        
        try:
            person = await app.get_users(userid)
            userid = person.id
        except Exception as e:
            await app.send_message(DIMA, f'Ошибка в get_user_id({userid})\n\n{e}')
            pass
        
        return userid
    
    
    async def check_if_a_user(message):
        
        if message.chat.type == ChatType.PRIVATE:
            dm_state = sql_select(f"SELECT active FROM users WHERE id = {message.from_user.id}")
            
            if dm_state:
                if dm_state[0][0] == 1:
                    return True
                else:
                    sql_edit('UPDATE users SET active = 1 WHERE id == ?;', (message.chat.id,))
            else:
                sql_edit('INSERT INTO users VALUES(?, ?);', (message.from_user.id, 1,))
        
        elif message.chat.type == ChatType.SUPERGROUP \
                or message.chat.type == ChatType.GROUP:
            group_state = sql_select(f"SELECT * FROM groups WHERE id = {message.chat.id}")
            
            if group_state:
                return True
            else:
                sql_edit('INSERT INTO groups VALUES(?, ?, ?, ?, ?);', (message.chat.id, 1, -1, 1, 1))
        
        else:
            
            return
    
    
    async def log(text):
        return await app.send_message(-1001652069822, text)
    
    
    async def scam_chances(person, scam_chance):
        
        if person.id < 6000000000:
            scam_chance -= 5
        
        if person.username:
            scam_chance -= 5
        
        if person.is_scam:
            scam_chance += 5
        
        if person.is_premium:
            scam_chance -= 10
        
        try:
            channel_status = await app.get_chat_member(chat_id=-1001513425824, user_id=person.id)
            group_status = await app.get_chat_member(chat_id=-1001740473921, user_id=person.id)

            if channel_status.status != ChatMemberStatus.LEFT and group_status.status != ChatMemberStatus.LEFT:
                return True
        
        except Exception:
            pass
        
        for symbol in support_symbols:
            if symbol in person.first_name or person.last_name and symbol in person.last_name:
                scam_chance -= 5
                break
        
        if '#газдсила' in person.first_name.lower() or person.last_name and \
                '#газдсила' in person.last_name.lower():
            scam_chance -= 5
        
        if not person.photo:
            scam_chance += 5
        
        if 'гарант' in person.first_name.lower() or person.last_name and \
                'гарант' in person.last_name.lower():
            scam_chance += 2
        
        if 'garant' in person.first_name.lower() or person.last_name and \
                'garant' in person.last_name.lower():
            scam_chance += 3
        
        if '#газдхуйня' in person.first_name.lower() or person.last_name and \
                '#газдхуйня' in person.last_name.lower():
            scam_chance += 14
        
        for symbol in ['[RT]', 'RT', 'ℝ𝕋', 'ᴿᵀ', '🅡🅣', 'ⓇⓉ', '𝒓𝒕', '𝐫𝐭', '𝕣𝕥', '𝚛𝚝', 'ʀᴛ', 'ʳᵗ',
                       'ᖇT', '🇷 🇹', '🅁🅃', '🆁🆃', '𝘳𝓽', '尺ㄒ', 'ዪፕ', 'ᏒᎢ', 'ʀⲧ', 'РТ',
                       'sᴀ', '𝕊𝔸', 'SA', '𝐒𝐀', 'Տᗩ', '𝑺𝑨', '#SA', ]:
            if symbol.lower() in person.first_name.lower() or person.last_name and \
                    symbol in person.last_name.lower():
                scam_chance += 10
                break
        
        if scam_chance > 99:
            scam_chance = 99
        
        return scam_chance
    
    
    async def check_sub(msg):
        
        if not await flyer.check(msg.from_user.id):
            return False
        else:
            return True
        
        # if await bot_id() != 6066255260:
        #     return True
        #
        # our_group = await app.get_chat(report_group)
        # our_channel = await app.get_chat(channel)
        #
        # keyboard = InlineKeyboardMarkup(
        #     [[InlineKeyboardButton("НАШ КАНАЛ 📣", url=f"tg://resolve?domain={our_channel.username}"),
        #       InlineKeyboardButton("ГРУППА ЖАЛОБ 💬", url=f"tg://resolve?domain={our_group.username}")],
        #      [InlineKeyboardButton('ГОТОВО ✅', callback_data=action)]])
        #
        # try:
        #
        #     channel_status = await app.get_chat_member(chat_id=-1001513425824, user_id=msg.from_user.id)
        #     group_status = await app.get_chat_member(chat_id=-1001740473921, user_id=msg.from_user.id)
        #
        #     if channel_status.status != ChatMemberStatus.LEFT and group_status.status != ChatMemberStatus.LEFT:
        #         return True
        #
        #     else:
        #         kb = []
        #         sub_to_text = 'на наш канал и нашу группу'
        #
        #         if channel_status.status == ChatMemberStatus.LEFT:
        #             kb.append(InlineKeyboardButton(
        #                 "НАШ КАНАЛ 📣", url=f"tg://resolve?domain={our_channel.username}"))
        #             sub_to_text = 'на наш канал'
        #
        #         if group_status.status == ChatMemberStatus.LEFT:
        #             kb.append(InlineKeyboardButton(
        #                 "ГРУППА ЖАЛОБ 💬", url=f"tg://resolve?domain={our_group.username}"))
        #
        #             if kb:
        #                 sub_to_text = 'на наш канал и нашу группу'
        #             else:
        #                 sub_to_text = 'на нашу группу жалоб'
        #
        #         keyboard = InlineKeyboardMarkup([kb, [InlineKeyboardButton('ГОТОВО ✅', callback_data=action)]])
        #
        #         await sent.edit(
        #             f"{msg.from_user.mention}, для продолжения нужно подписаться {sub_to_text} 👇",
        #             reply_markup=keyboard)
        #         await app.send_message(DIMA, f'Проверка подписки правильно отработала\n\n{sub_to_text}')
        #         return False
        #
        # except errors.UserNotParticipant:
        #
        #     await sent.edit(
        #         f"{msg.from_user.mention}, для продолжения нужно подписаться на наш чат и канал 👇",
        #         reply_markup=keyboard)
        #     await app.send_message(DIMA, f'Проверка подписки:\n\nUserNotParticipant')
        #     return False
        #
        # except Exception as e:
        #
        #     await sent.edit(
        #         f"{msg.from_user.mention}, для продолжения нужно подписаться на наш чат и канал 👇",
        #         reply_markup=keyboard)
        #
        #     await app.send_message(chat_id=1032156461, text=f'🪢 Ошибка при проверке подписки: {e}')
        #     return False
    
    
    async def new_search(userid):
        user_state = sql_select(f"SELECT * FROM net WHERE id = {userid}")
        
        if not user_state:
            sql_edit(f'INSERT INTO net VALUES(?,?,?,?,?,?,?,?,?);',
                     (userid, 1, "Bio hasn't been set yet ☃️", "None 🦛", "❓", None, 0, 0, 0))
            return sql_select(f"SELECT * FROM net WHERE id = {userid}")
        if user_state:
            sql_edit(f'UPDATE net SET searches=searches+1 WHERE id = {userid};', ())
            return sql_select(f"SELECT * FROM net WHERE id = {userid}")
    
    
    async def add_to_net(userid):
        user_state = sql_select(f"SELECT * FROM net WHERE id = {userid}")
        
        if not user_state:
            sql_edit(f'INSERT INTO net VALUES(?,?,?,?,?,?,?,?,?,?,?);',
                     (userid, 1, "Bio hasn't been set yet ☃️", "None 🦛", "❓", None, 0, 0, 0, 2, 10))
            return sql_select(f"SELECT * FROM net WHERE id = {userid}")
        else:
            return user_state
    
    
    async def check_person_by_id(person):
        
        try:
            
            user_state = await new_search(person.id)
            country = get_country(user_state[0][3])
            if not country:
                country = f' <a href=https://t.me/AntiScamRoblox/432>Не задана {random.choice(lol)}</a>'
            
            _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {person.id}")
            
            if _fetchall_mms:
                await update_stats(person)
                
                popularity = sql_select(f"SELECT * FROM daily_searches "
                                        f"WHERE id={person.id}")
                
                if not popularity:
                    sql_edit(f'INSERT INTO daily_searches VALUES(?, ?)', (person.id, 1))
                else:
                    sql_edit(f'UPDATE daily_searches SET searches=searches+1 '
                             f'WHERE id={person.id}', ())
                connection.commit()
                
                return f'''
Информация о {person.mention} [<code>{person.id}</code>]
<a href={themes['default']['mm']}>\u200B</a>
💙 <b>Репутация</b>: Гарант ✅
<a href=https://t.me/AntiScamRoblox/301>❓ Кто такой гарант?</a>

📣 <b>Канал гаранта</b>: {user_state[0][4]}
🌎 <b>Страна</b>: {country}
🌴 <b>Тег:</b> @{person.username}
🔥 Скаммеров слито: {user_state[0][8]}

🔍 Искали {user_state[0][1]} раз
🗓 Проверено {await get_date()}'''
            
            _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {person.id}")
            
            if _fetchall_admins:
                
                if person.id == 1032156461:
                    role = '💪🔥 ПАПА'
                elif _fetchall_admins[0][2] == 0:
                    role = '🍼👶 Стажёр'
                elif _fetchall_admins[0][2] == 1:
                    role = '👋🤓 Администратор'
                elif _fetchall_admins[0][2] == 2:
                    role = '🔥🥸 Директор'
                elif _fetchall_admins[0][2] == 3:
                    role = '🏆😎 Президент'
                else:
                    role = '❓❓ Долбоёб'
                
                await update_stats(person)
                return f'''
Информация о {person.mention} [<code>{person.id}</code>]
<a href={themes['default']['staff']}>\u200B</a>
💙 Персонал <a href=AntiScamDatabaseBot.t.me>GASD</a>
📊 {role} | ⚠️{_fetchall_admins[0][1]} | ✅{_fetchall_admins[0][3]}

📣 <b>Канал волонтёра</b>: {user_state[0][4]}
🌎 <b>Страна</b>: {country}

🔍 Искали {user_state[0][1]} раз
🗓 Проверено {await get_date()}'''
            
            if user_state[0][6] > 0:
                await update_stats(person)
                
                popularity = sql_select(f"SELECT * FROM daily_searches WHERE id={person.id}")
                
                if not popularity:
                    sql_edit(f'INSERT INTO daily_searches VALUES(?, ?)', (person.id, 1))
                else:
                    sql_edit(f'UPDATE daily_searches SET searches=searches+1 WHERE id={person.id}', ())
                
                scam_chance = await scam_chances(person, 36)
                
                return f'''
Информация о {person.mention} [<code>{person.id}</code>]
<a href={themes['default']['trusted']}>\u200B</a>
💙 <b>Репутация</b>: Проверен(а) гарантом {(await app.get_users(user_state[0][6])).mention} ✅
<a href=https://t.me/AntiScamRoblox/301>❓ Кто такой гарант?</a>

❓ Вероятность скама: {scam_chance}%
🌎 <b>Страна</b>: {country}
🔥 Скаммеров слито: {user_state[0][8]}

🔍 Искали {user_state[0][1]} раз
🗓 Проверено {await get_date()}'''
            
            _fetchall_scammers = sql_select(f"SELECT * FROM scammers WHERE id = {person.id}")
            
            if _fetchall_scammers:
                _fetchall_scammers[0][3].replace('ReportRoblox', 'GasdReport')
                await update_stats(person)
                
                if _fetchall_scammers[0][2] == 'СКАММЕР ⚠':
                    return f'''
Информация о {person.mention} [<code>{person.id}</code>]
<a href={themes['default']['scam']}>\u200B</a>
💙 <b>Репутация</b>: {_fetchall_scammers[0][2]}
❓ Вероятность скама: 99%
📚 <b>Описание</b>: {_fetchall_scammers[0][3]}

🌎 <b>Страна</b>: {country}

🔍 Искали {user_state[0][1]} раз
🗓 Проверено {await get_date()}'''
                else:
                    
                    scam_chance = await scam_chances(person, 70)
                    
                    return f'''
Информация о {person.mention} [<code>{person.id}</code>]
<a href={themes['default']['high_scam_chances']}>\u200B</a>
💙 <b>Репутация</b>: {_fetchall_scammers[0][2]}
❓ Вероятность скама: {scam_chance}%
📚 <b>Описание</b>: {_fetchall_scammers[0][3]}

🌎 <b>Страна</b>: {country}

🔍 Искали {user_state[0][1]} раз
🗓 Проверено {await get_date()}'''
            
            
            else:
                await update_stats(person)
                
                scam_chance = await scam_chances(person, 45)
                
                return f'''
Информация о {person.mention} [<code>{person.id}</code>]
<a href={themes['default']['no_data']}>\u200B</a>
❓ Человека нет в базе! Вероятность скама: {scam_chance}%

🌎 <b>Страна</b>: {country}
🔥 Скаммеров слито: {user_state[0][8]}

<i>👍 Будьте аккуратны и всегда используйте проверенных гарантов, не ведитесь на обман!</i>

🔍 Искали {user_state[0][1]} раз
🗓 Проверено {await get_date()}'''
        
        except Exception as e:
            
            await app.send_message(1032156461,
                                   f'Got an error while trying to use "check_person_by_id".\n\n<pre>{e}</pre>')
            return


    async def update_stats(person):
        global the_most_recent_search
        the_most_recent_search = person.mention
    
    
    async def if_supports_gasd(person, chat_id):
        for symbol in support_symbols:
            if symbol in person.first_name or person.last_name and symbol in person.last_name:
                await app.send_message(chat_id,
                                       f'✅ || {person.mention} <b>поддерживает борьбу со скамом</b>, установив в ник '
                                       f'символ <code>{symbol}</code>\n======\n (<i>Нажмите на <code>{symbol}</code>,'
                                       f' чтобы скопировать и поставить к себе в ник</i>)')
                break
    
    
    async def if_hedgehog(person, chat_id):
        if '🦔' in person.first_name or person.last_name and '🦔' in person.last_name:
            await app.send_message(chat_id,
                                   f'✅ || {person.mention} <b>просто ёжик 🦔</b>, это абсолютно ничего не значит, '
                                   f'просто милый ёжик :)\n\nЗалетайте кстати в наш '
                                   f'<a href=t.me/YozhChat>🔥 Ежиный Чат</a>')
    
    async def admin_limits(message, cooldown):
        if not message.from_user:
            return False
        
        if message.from_user.id in adm_limits and adm_limits[message.from_user.id] + cooldown >= time.time():
            await message.reply(
                f'<b>❌ Подождите {round((adm_limits[str(message.from_user.id)] + cooldown) - time.time())} секунд</b>',
                reply_markup=HIDE_KB)
            return False
        
        adm_limits[message.from_user.id] = time.time()
        return True
    
    
    @app.on_chat_join_request()
    async def trigger(_, update):
        
        mm_groups = (-1002101027116,)
        admin_groups = (-1002091856799, -1001652069822, -1001773900560)
        
        if update.chat.id in mm_groups:
            
            _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {update.from_user.id}")
            
            if _fetchall_mms:
                await update.approve()
                await app.send_message(update.from_user.id, 'Поздравляем, ваша заявка была одобрена 😏',
                                       reply_markup=HIDE_KB)
            else:
                await update.decline()
                await app.send_message(
                    update.from_user.id, 'ℹ️ Доступно только гарантам нашей базы', reply_markup=HIDE_KB)
        
        elif update.chat.id in admin_groups:
            
            _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {update.from_user.id}")
            
            if _fetchall_admins:
                await update.approve()
                await app.send_message(update.from_user.id, 'Заявка была одобрена 👌',
                                       reply_markup=HIDE_KB)
            else:
                await update.decline()
                await app.send_message(
                    update.from_user.id, 'Доступно только админам нашей базы', reply_markup=HIDE_KB)
    
    @app.on_message(filters.command('start', ["/"]) & filters.text)
    async def answer(_, message):
        
        commands.start += 1
        await check_if_a_user(message)
        
        await message.reply('👋')
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        
        if message.chat.type == ChatType.PRIVATE:
            await message.reply(
                text=f'<a href=https://telegra.ph/file/3b7d4756d4026a1915d4c.png>\u200B</a>\n'
                     f'<b>Мы - <a href="t.me/AntiScamDatabaseBot">ГАЗД</a>, '
                     "Глобальная АнтиСкам База нового поколения:</b>\n\n"
                     '🤓 Проверим человека на скам\n'
                     '🤠 Найдём проверенного гаранта\n'
                     '🤕 Поможем слить скаммера\n\n'
                     'ℹ️ <i>Используйте кнопки ниже для диалога с ботом</i>',
                reply_markup=DEFAULT_KB)
            
        else:
            await message.reply(
                text=f'<a href=https://telegra.ph/file/3b7d4756d4026a1915d4c.png>\u200B</a>\n'
                     f'<b>Мы - <a href="t.me/AntiScamDatabaseBot">ГАЗД</a>, '
                     "Глобальная АнтиСкам База нового поколения:</b>\n\n"
                     '🤓 Проверим человека на скам\n'
                     '🤠 Найдём проверенного гаранта\n'
                     '🤕 Поможем слить скаммера\n\n'
                     'ℹ️ <i>Чтобы проверить человека прямо в чате, ответьте <b>чек</b> в ответ на его сообщение</i>',
                reply_markup=DEFAULT_KB)
        
        try:
            await app.delete_messages(message.chat.id, message.id)
        except MessageDeleteForbidden:
            await message.reply('<i>🌴 Для полноценной работы боту нужна админка</i>')
        except Exception as e:
            await message.reply('<i>🌴 Для полноценной работы боту нужна админка</i>')
            await app.send_message(DIMA, f'Ошибка при удалении сообщения:\n\n<pre>{e}</pre>')
            
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(1)
        
        if message.chat.type == ChatType.PRIVATE:
            await message.reply(
                '❤️ Спасибо за выбор нашего бота проверки на скам\n\n'
                '🐳 <b>Попробуйте проверить человека</b> - напишите "<code>чек @BrandAPI</code>" (без кавычек)',
                reply_markup=MAIN_KB)
        else:
            await message.reply('❤️ Спасибо за выбор нашего бота проверки на скам')
        return
    
    @app.on_message(filters.command(
        ['unban', 'разбан', 'разбанить', 'анбан', 'unmute', 'размут', 'размутить', 'анмут'],
        ["/", "!"]) & filters.text)
    async def answer(_, message):
        user_status = (await app.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)).status
        
        if user_status == ChatMemberStatus.OWNER or user_status == ChatMemberStatus.ADMINISTRATOR:
            if message.reply_to_message:
                person_to_unban = message.reply_to_message.from_user
            else:
                args = message.text.split()
                
                if len(args) < 2:
                    await message.reply('❌ Вы не указали, кого хотите разбанить')
                    return
                else:
                    person_to_unban = (await app.get_chat_member(message.chat.id, args[1])).user
            
            try:
                await app.unban_chat_member(message.chat.id, person_to_unban.id)
                
                await message.reply(f'✅ {person_to_unban.mention} был разбанен')
            except ChatAdminRequired:
                await message.reply(f'❌ Дайте мне админку, без неё я не смогу разбанить')
            except Exception as e:
                await message.reply(f'Произошла ошибка: <pre>{e}</pre>')
    
    @app.on_message(filters.command(['ban', 'бан'], ["/", "!"]) & filters.text)
    async def answer(_, message):
        user_status = (await app.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)).status
        
        if user_status == ChatMemberStatus.OWNER or user_status == ChatMemberStatus.ADMINISTRATOR:
            
            message.text = message.text.lower()
            args = message.text.split()
            
            bantime = None
            bantext = 'навсегда'
            
            if message.reply_to_message:
                person_to_ban = message.reply_to_message.from_user
                
                if len(args) > 1:
                    if args[1].endswith('m') or args[1].endswith('minutes') \
                            or args[1].endswith('м') or args[1].endswith('минут'):
                        bantime = timedelta(minutes=int(args[1][:-1]))
                        bantext = f'на {args[1][:-1]} минут'
                        
                    if args[1].endswith('h') or args[1].endswith('hours') \
                            or args[1].endswith('ч') or args[1].endswith('часов'):
                        bantime = timedelta(hours=int(args[1][:-1]))
                        bantext = f'на {args[1][:-1]} часов'
                        
                    if args[1].endswith('d') or args[1].endswith('days') \
                            or args[1].endswith('д') or args[1].endswith('дней'):
                        bantime = timedelta(days=int(args[1][:-1]))
                        bantext = f'на {args[1][:-1]} дней'
            else:
                if len(args) < 2:
                    await message.reply('❌ Вы не указали, кого хотите забанить')
                    return
                else:
                    person_to_ban = (await app.get_chat_member(message.chat.id, args[1])).user
                    
                    if len(args) > 2:
                        if args[2].endswith('m') or args[2].endswith('minutes') \
                                or args[2].endswith('м') or args[2].endswith('минут'):
                            bantime = timedelta(minutes=int(args[2][:-2]))
                            bantext = f'на {args[2][:-2]} минут'
                        
                        if args[2].endswith('h') or args[2].endswith('hours') \
                                or args[2].endswith('ч') or args[2].endswith('часов'):
                            bantime = timedelta(hours=int(args[2][:-2]))
                            bantext = f'на {args[2][:-2]} часов'
                        
                        if args[2].endswith('d') or args[2].endswith('days') \
                                or args[2].endswith('д') or args[2].endswith('дней'):
                            bantime = timedelta(days=int(args[2][:-2]))
                            bantext = f'на {args[2][:-2]} дней'
            
            try:
                if bantime:
                    await app.ban_chat_member(message.chat.id, person_to_ban.id, datetime.now() + bantime)
                else:
                    await app.ban_chat_member(message.chat.id, person_to_ban.id)
            
                await message.reply(f'⛔ {person_to_ban.mention} был забанен {bantext}')
            except ChatAdminRequired:
                await message.reply(f'❌ Дайте мне админку, без неё я не могу банить')
            except UserAdminInvalid:
                await message.reply(f'❌ Нельзя банить админов')
            except Exception as e:
                await message.reply(f'Произошла ошибка: <pre>{e}</pre>')
        else:
            await message.reply('❌ Вы не админ в чате')
            return
          
    @app.on_message(filters.command(['mute', 'мут'], ["/", "!"]) & filters.text)
    async def answer(_, message):
        user_status = (await app.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)).status
        
        if user_status == ChatMemberStatus.OWNER or user_status == ChatMemberStatus.ADMINISTRATOR:
            
            message.text = message.text.lower()
            args = message.text.split()
            
            bantime = None
            bantext = 'навсегда'
            
            if message.reply_to_message:
                person_to_ban = message.reply_to_message.from_user
                
                if len(args) > 1:
                    if args[1].endswith('m') or args[1].endswith('minutes') \
                            or args[1].endswith('м') or args[1].endswith('минут'):
                        bantime = timedelta(minutes=int(args[1][:-1]))
                        bantext = f'на {args[1][:-1]} минут'
                        
                    if args[1].endswith('h') or args[1].endswith('hours') \
                            or args[1].endswith('ч') or args[1].endswith('часов'):
                        bantime = timedelta(hours=int(args[1][:-1]))
                        bantext = f'на {args[1][:-1]} часов'
                        
                    if args[1].endswith('d') or args[1].endswith('days') \
                            or args[1].endswith('д') or args[1].endswith('дней'):
                        bantime = timedelta(days=int(args[1][:-1]))
                        bantext = f'на {args[1][:-1]} дней'
            else:
                if len(args) < 2:
                    await message.reply('❌ Вы не указали, кого хотите замутить')
                    return
                else:
                    person_to_ban = (await app.get_chat_member(message.chat.id, args[1])).user
                    
                    if len(args) > 2:
                        if args[2].endswith('m') or args[2].endswith('minutes') \
                                or args[2].endswith('м') or args[2].endswith('минут'):
                            bantime = timedelta(minutes=int(args[2][:-2]))
                            bantext = f'на {args[2][:-2]} минут'
                        
                        if args[2].endswith('h') or args[2].endswith('hours') \
                                or args[2].endswith('ч') or args[2].endswith('часов'):
                            bantime = timedelta(hours=int(args[2][:-2]))
                            bantext = f'на {args[2][:-2]} часов'
                        
                        if args[2].endswith('d') or args[2].endswith('days') \
                                or args[2].endswith('д') or args[2].endswith('дней'):
                            bantime = timedelta(days=int(args[2][:-2]))
                            bantext = f'на {args[2][:-2]} дней'
            
            try:
                if bantime:
                    await app.restrict_chat_member(
                        message.chat.id, person_to_ban.id,
                        ChatPermissions(can_send_messages=False), datetime.now() + bantime)
                else:
                    await app.restrict_chat_member(
                        message.chat.id, person_to_ban.id, ChatPermissions(can_send_messages=False))
            
                await message.reply(f'⛔ {person_to_ban.mention} был замучен {bantext}')
            except ChatAdminRequired:
                await message.reply(f'❌ Дайте мне админку, без неё я не могу мутить')
            except UserAdminInvalid:
                await message.reply(f'❌ Нельзя мутить админов')
            except Exception as e:
                await message.reply(f'Произошла ошибка: <pre>{e}</pre>')
        else:
            await message.reply('❌ Вы не админ в чате')
            return
    
    @app.on_message(filters.command(['del', 'дел'], ["/", ""]) & filters.text)
    async def answer(_, message):
        
        if not await admin_limits(message, 10):
            return
        
        _fetchall_admins = sql_select(f"SELECT status FROM admins WHERE id = {message.from_user.id}")
        
        if (_fetchall_admins and _fetchall_admins[0][0] > 0) or message.from_user.id == 1032156461:
            msg = message.text.split()
            
            if len(msg) > 1:
                
                msg[1] = await get_user_id(msg[1])
                
                try:
                    
                    _fetchall_scammers = sql_select(f"SELECT * FROM scammers WHERE id = {msg[1]}")
                    if _fetchall_scammers:
                        
                        sql_edit(f'DELETE FROM scammers WHERE id = {msg[1]}', ())
                        
                        try:
                            await app.send_message(msg[1], '👀 Ваша репутация в базе была изменена',
                                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                       text='Чекнуть себя 🔎',
                                                       callback_data=f'check {msg[1]}'
                                                   )]]))
                            commands.changed += 1
                        
                        except Exception as e:
                            await app.send_message(DIMA, f'⛔ Не получилось отправить уведомление!\n\n<pre>{e}</pre>')
                        
                        posted_message = await app.send_message(
                            -1001652069822,
                            f'Админ {message.from_user.mention} удалил человека из базы!\n\n'
                            f'#id{message.from_user.id} #удаление_из_бд\n=============\n'
                            f'Данные о пользователе:\n🆔 <code>{msg[1]}</code>\n'
                            f'<a href=tg://openmessage?user_id={msg[1]}>Вечная Ссылка</a>')
                        await message.reply(
                            f'<b>👋 | Успешно удалил '
                            f'<a href=tg://openmessage?user_id={msg[1]}>пользователя из базы.</a></b>'
                            f'\n\nℹ️ https://t.me/c/{str(posted_message.chat.id)[3:]}/{posted_message.id}')
                    
                    else:
                        await message.edit(f"Пользователя с ID {msg[1]} нет в нашей базе данных",
                                           reply_markup=HIDE_KB)
                except Exception as e:
                    
                    await message.edit("Что-то пошло не так", reply_markup=HIDE_KB)
                    await message.edit(e, reply_markup=HIDE_KB)
            else:
                await message.edit("⛔ Пример команды: /del @onetimeusername", reply_markup=HIDE_KB)
                return

        else:
            await message.reply("⛔ Только админы могут использовать эту команду!", reply_markup=HIDE_KB)
            return
    
    @app.on_message(filters.command('Тех Поддержка ⚙️', [""]) & filters.text)
    async def answer(_, message):
        if message.chat.type == ChatType.PRIVATE:
            await message.reply(f'⚙ {message.from_user.mention}, используйте кнопки ниже для навигации:',
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton('Сообщить о баге 🐞', callback_data='bugreport')],
                                    [InlineKeyboardButton('Предложить идею 💡', callback_data='idea')],
                                    [InlineKeyboardButton('Оставить отзыв 🦔💬', callback_data='vouch')],
                                    [InlineKeyboardButton('Пожаловаться на проблему 😥', callback_data='gotatrouble')]]))
        else:
            await message.reply('⚠️ Данный функционал работает только в личке с ботом',
                                reply_markup=InlineKeyboardMarkup(
                                    [[InlineKeyboardButton('Перейти ➡️', callback_data='dms')]]))
    
    
    @app.on_message(filters.command(["Гаранты ❤️‍🔥", "/mms"], ['']) & filters.text)
    async def answer(_, message):
        
        commands.mms += 1
        if message.from_user.id in banned:
            await message.reply('ℹ️ Пожалуйста, дождитесь выполнения прошлого запроса')
            return
        
        banned.append(message.from_user.id)
        
        mms = sql_select(f"SELECT id FROM mms")
        buttons = []
        
        msg = await message.reply(f'⏳ {message.from_user.mention}, загружаем...\n\nℹ️ {random.choice(hints)}')
        
        for mm in mms:
            user_state = await new_search(mm[0])
            
            try:
                person = await app.get_users(mm[0])
                buttons.append([InlineKeyboardButton(text=f' {person.first_name} | 🔎 {user_state[0][1]}',
                                                     callback_data=f'check {mm[0]}')])
            
            except Exception as e:
                await app.send_message(DIMA, f'Ошибка при формировании списка гарантов\n\n{e}')
        
        buttons.append([InlineKeyboardButton('КТО ТАКОЙ ГАРАНТ? 🤓', url='https://t.me/AntiScamRoblox/301')])
        buttons.append([InlineKeyboardButton("СТАТЬ ГАРАНТОМ 🦔", callback_data="become mm")])
        
        await msg.edit(text='❤️‍🔥 Ниже список гарантов нашей базы, им можно доверять',
                       reply_markup=InlineKeyboardMarkup(buttons))
        banned.remove(message.from_user.id)
    
    @app.on_message(filters.command(["Волонтёры 🌴", "/admins"], ['']) & filters.text)
    async def answer(_, message):
        commands.admins += 1
        
        if message.from_user.id in banned:
            await message.reply('ℹ️ Пожалуйста, дождитесь выполнения прошлого запроса')
            return
        
        banned.append(message.from_user.id)
        
        admins = sql_select(f"SELECT id, status FROM admins")
        text = f'💪 <b>Админы ГАЗДа ({len(admins)} / 25):</b>\n'
        buttons = []
        
        msg = await message.reply(f'⏳ {message.from_user.mention}, загружаем...\n\nℹ️ {random.choice(hints)}')
        
        for admin in admins:
            try:
                
                person = await app.get_users(admin[0])
                
                if admin[1] == 0:
                    role = '🍼👶'
                elif admin[1] == 1:
                    role = '👋🤓'
                elif admin[1] == 2:
                    role = '🔥🥸'
                elif admin[1] == 3:
                    role = '🏆😎'
                else:
                    role = '❓❓'
                
                buttons.append([InlineKeyboardButton(text=f'{role} {person.first_name}',
                                                     callback_data=f'check {admin[0]}')])
            
            except Exception as e:
                await app.send_message(DIMA, f'Ошибка при составлении списка админов\n\n{e}')
                pass
        
        buttons.append([InlineKeyboardButton("Как стать волонтёром?", callback_data="become admin")])
        await msg.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))
        
        banned.remove(message.from_user.id)
    
    @app.on_message(filters.command(['Помощь 🤓', '/help'], ['']) & filters.text)
    async def answer(_, message):
        
        commands.help += 1
        
        await app.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)
        await app.send_video(
            chat_id=message.chat.id,
            video='BAACAgIAAxkDAAEE8jlkqVpmXjQIgMTJyg-OY_6FKnWSGQAC-jMAAuQEUEn_RdEmWrw4pB4E',
            caption='''
Я - GASD 💪🧬, бот, помогающий проверять людей на скам и сливать скаммеров.

Ниже перечислены мои основные команды:

💠 /start
- <i>Перезапуск бота, если пропали кнопки</i>

💠 чек (@юзер ИЛИ ID проверяемого, без скобок)
- <i>Проверить человека на скам</i>

💠 чек я
- <i>Проверить СЕБЯ</i>

<b>Остальной функционал доступен по кнопкам в меню</b>

Слить скаммера - @GasdReport
                ''',
            reply_markup=DEFAULT_KB)
        return
    
    
    @app.on_message(filters.command(['FAQ ❓', '/help'], ['']) & filters.text)
    async def answer(_, message):
        
        await message.reply('💁‍♂️ Выберите вопрос из списка ниже:', reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('🤔 Кто такой гарант?', callback_data='faq 1')],
             [InlineKeyboardButton('🔍 Как найти гаранта?', callback_data='faq 2')],
             [InlineKeyboardButton('🛡 Как стать админом?', callback_data='faq 3')],
             [InlineKeyboardButton('✅ Как стать гарантом?', callback_data='faq 4')],
             [InlineKeyboardButton('😡 Как слить скаммера?', callback_data='faq 5')],
             [InlineKeyboardButton('⌚ Когда набор на админов?', callback_data='faq 6')],
             [InlineKeyboardButton('💸 Можно ли купить роль в базе?', callback_data='faq 7')],
             [InlineKeyboardButton('💰 Можно ли купить снятие из базы?', callback_data='faq 8')], ]
        ))
        return
    
    
    @app.on_message(filters.command(['Не оффтопьте'], [""]))
    async def action(_, message):
        if message.reply_to_message and message.chat.id == -1001740473921:
            _fetchall_admins = sql_select(f"SELECT id FROM admins WHERE id = {message.from_user.id}")
            
            if _fetchall_admins:
                try:
                    await app.restrict_chat_member(-1001740473921,
                                                   message.reply_to_message.from_user.id,
                                                   ChatPermissions(can_send_messages=False),
                                                   datetime.now() + timedelta(minutes=5))
                    await message.reply_to_message.reply(
                        'Этот чат предназначен для слива скаммеров, '
                        'а для общения у нас есть отдельный чат - @GasdChat\n\n'
                        'Мут будет снят через 5 минут, спасибо за понимание ❤️',
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                            '🌴 Чат общения', url='https://t.me/+wxf_44fe5cE4MjY6')]]))
                    
                except Exception as e:
                    await app.send_message(DIMA, f'Ошибка в муте за оффтоп\n\n<pre>{e}</pre>')
            else:
                await message.reply('<b>❌ Доступно только админам</b>')
    
    @app.on_message(filters.command(['Статистика', '/stats'], [""]) & filters.text)
    async def answer(_, message):
        
        if message.from_user.id in banned:
            await message.reply(
                f'<b>❌ Эта команда имеет ограничение на скорость!</b>\n'
                f'Пожалуйста, дождитесь выполнения прошлого запроса, а затем вызывайте команду снова.',
                reply_markup=HIDE_KB)
            return
        
        commands.stats += 1
        banned.append(message.from_user.id)
        
        global the_most_recent_search
        
        await message.reply(f'''
{message.from_user.mention}, ниже находится статистика нашего бота:
<a href=https://telegra.ph/file/cff90a1e4873fe560010e.png>\u200B</a>
🚫 Скаммеров в базе: {sql_select("SELECT COUNT(id) from scammers;")[0][0]}
👁️ Пользователей бота: {sql_select("SELECT COUNT(id) from users WHERE active=1;")[0][0]}

⚖️ Админов: {sql_select("SELECT COUNT(id) from admins;")[0][0]}
💸 Гарантов: {sql_select("SELECT COUNT(id) from mms;")[0][0]}
🏆️ Проверенных: {sql_select("SELECT COUNT(id) from net WHERE is_trusted > 0;")[0][0]}

🎉 Бот уже в {sql_select("SELECT COUNT(id) from groups;")[0][0]} группах

🔎 Поисков по базе за всё время: {sql_select("SELECT SUM(searches) from net WHERE searches > 0")[0][0]}
🌴 В последний раз искали: {the_most_recent_search}
        ''', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Топ по сливам 🌴', callback_data='top_reporters')],
            [InlineKeyboardButton('Топ админов 😎', callback_data='top_admins'),
             InlineKeyboardButton('Топ популярных 🐱', callback_data='top_mms')]]))
        
        if message.from_user.id == DIMA:
            await message.reply(f'{commands}')
        banned.remove(message.from_user.id)
        return
    
    
    @app.on_message(filters.command(['check', 'чек', 'проверить', 'chek'], ["/", ""]) & filters.text)
    async def answer(_, message):
        
        await add_to_net(message.from_user.id)
        
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        data = sql_select(f'SELECT free_checks FROM net WHERE id = {message.from_user.id}')
        
        if (data and data[0][0] > 0) or _fetchall_admins:
            
            sent = await message.reply(f'⏳ {message.from_user.mention}, загружаем...'
                                       f'<a href={themes["default"]["loading"]}>\u200B</a>\n\nℹ️ {random.choice(hints)}')
            msg = message.text.split()
            commands.check += 1
            
            try:
            
                # определяем, кого проверять
                
                if message.reply_to_message:
                    person = message.reply_to_message.from_user
                    
                elif len(msg) == 1:
                    
                    await sent.edit(
                        "<a href=https://telegra.ph/file/4af854abf55a4cd8eb52f.png>\u200B</a>"
                        f"Введите @юзернейм человека, которого хотите проверить!\n\n"
                        f"Например:\n<pre>/check @onetimeusername</pre>")
                    return
                
                elif msg[1] in ('me', 'myself', 'ми', 'меня', 'я', 'себя'):
                    person = message.from_user
                    
                else:
                    if msg[1].startswith('https://t.me/'):
                        msg[1] = str(msg[1][13:])
                    if msg[1].startswith('t.me/'):
                        msg[1] = str(msg[1][5:])
                    
                    msg[1] = re.sub('[^A-Za-z0-9_]', '', msg[1])
                    
                    if msg[1]:
                        person = await app.get_users(msg[1])
                    else:
                        return
                
                # проверяем
                if message.chat.type == ChatType.PRIVATE:
                    if not await check_sub(message):
                        return
                
                res = await check_person_by_id(person)
                
                if res:
                    if sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}"):
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton(
                            text='Вынести из базы ❌',
                            callback_data=f'del {person.id}')]])
                    else:
                        if message.from_user.id == person.id:
                            
                            scamdata = sql_select(f"SELECT * FROM scammers WHERE id = {message.from_user.id}")
                            netdata = sql_select(f"SELECT * FROM net WHERE id = {message.from_user.id}")
                            
                            if scamdata and netdata and netdata[0][7] == 0:
                                
                                if (scamdata[0][3].lower().startswith('поддержка скам груп') and len(scamdata[3]) < 64)\
                                        or scamdata[0][3].lower().startswith('отказ от гаранта') and len(scamdata[3]) < 64:
                                    
                                    kb = InlineKeyboardMarkup(
                                        [[InlineKeyboardButton(text='❌ ВЫЙТИ ИЗ БАЗЫ', callback_data=f'in_dev')]])
                                
                                else:
                                    kb = InlineKeyboardMarkup(
                                        [
                                            [InlineKeyboardButton(text='ℹ ПРОФИЛЬ ℹ️', user_id=message.from_user.id),
                                             InlineKeyboardButton(text='⚖️ АППЕЛЯЦИЯ ⚖️',
                                                                  callback_data=f'appeal {message.from_user.id}')],
                                            [InlineKeyboardButton(text='🔍 ПРОБИТЬ СКАММЕРА 🔍',
                                                                  url='https://t.me/MephEyeBot?start=1032156461')]
                                        ])
                                    
                            else:
                                kb = InlineKeyboardMarkup(
                                    [
                                        [InlineKeyboardButton(text='ℹ ПРОФИЛЬ ℹ️', user_id=message.from_user.id),
                                         InlineKeyboardButton(text='⚖️ АППЕЛЯЦИЯ ⚖️',
                                                              callback_data=f'appeal {message.from_user.id}')],
                                        [InlineKeyboardButton(text='🔍 ПРОБИТЬ СКАММЕРА 🔍',
                                                              url='https://t.me/MephEyeBot?start=1032156461')]
                                    ])
                                
                        else:
                            kb = InlineKeyboardMarkup([
                                [InlineKeyboardButton(text='ℹ ПРОФИЛЬ ℹ️', user_id=person.id)],
                                [InlineKeyboardButton(text='🔍 ПРОБИТЬ СКАММЕРА 🔍',
                                                      url='https://t.me/MephEyeBot?start=1032156461')]])
                    
                    try:
                        await sent.edit(res, reply_markup=kb)
                    except errors.ButtonUserPrivacyRestricted:
                        await sent.edit(res, reply_markup=AS_REPORT_KB)
                    
                    await if_hedgehog(person, message.chat.id)
                    await if_supports_gasd(person, message.chat.id)
                    
                    sql_edit(
                        f'UPDATE net SET free_checks = free_checks - 1 WHERE id = {message.from_user.id}', ())
                    
            except errors.UsernameInvalid:
                await sent.edit('''
❌ <b>Телеграм вернул ошибку: "Неправильный юзернейм"</b>

Возможно, пользователь сменил @юзернейм''',
                                reply_markup=AS_REPORT_KB)
                
            except errors.PeerIdInvalid:
                await sent.edit('''
❌ <b>Телеграм вернул ошибку: "Незнакомый чат"</b>

Невозможно получить айди этого пользователя, т.к. бот его не видел. Попробуйте проверить его по ID''',
                                reply_markup=AS_REPORT_KB)
            
            except errors.UsernameNotOccupied:
                await sent.edit('''
❌ <b>Телеграм вернул ошибку: "Юзернейм не занят"</b>

Такого юзернейма нет. Проверьте, не допустили ли вы ошибок при написании и не сменил ли скаммер тег''',
                                reply_markup=AS_REPORT_KB)
        
            except errors.FloodWait as e:
                
                minutes = round(e.value / 60)
                
                if minutes < 59:
                    
                    ending = ''
                    if minutes % 10 == 1:
                        ending = 'у'
                    elif minutes % 10 in (2, 3, 4):
                        ending = 'ы'
                
                    await sent.edit(f'❌ <b>Боту дали ограничение на проверку людей.</b> '
                                    f'Сейчас бот может проверять только тех, кто часто взаимодействовал с ботом\n\n'
                                    f'Попробуйте снова через ~{minutes} минут{ending}',
                                    reply_markup=AS_REPORT_KB)
                
                else:
                    
                    hours = round(minutes / 60)
                    
                    ending = 'ов'
                    if hours % 10 == 1:
                        ending = ''
                    elif hours % 10 in (2, 3, 4):
                        ending = 'а'
                    
                    await sent.edit(f'❌ <b>Боту дали ограничение на проверку людей.</b> '
                                    f'Сейчас бот может проверять только тех, кто часто взаимодействовал с ботом\n\n'
                                    f'Попробуйте снова через ~{hours} час{ending}',
                                    reply_markup=AS_REPORT_KB)
                
            except Exception as e:
                await sent.edit('❌ Не получилось проверить человека. Убедитесь, что вы правильно ввели команду!')
                await app.send_message(DIMA, f'Ошибка в /check\n\n<pre>{e}</pre>')
        else:
            await message.reply(f'<b>⌛ Вы превысили лимит проверок в день (10/10)</b>')
        
    
    @app.on_message(filters.command(['/close'], [""]) & filters.text)
    async def answer(_, message):
        
        peer = await app.resolve_peer(-1001949170455)
        try:
            await app.invoke(EditForumTopic(channel=peer, topic_id=message.reply_to_message_id, title=f'🔴', closed=True))
        except Exception as e:
            await message.reply(f'{e}')
        await app.send_message(
            -1001949170455,
            '<a href=https://telegra.ph/file/97faf8bb06675ffc3e764.png>\u200B</a>'
            f'<b>{message.from_user.mention} закрыл топик.</b>\n\n'
            f'Спасибо, что обратились к нам! Наш бот - @AntiScamDatabaseBot',
            reply_to_message_id=message.reply_to_message_id)
        
    
    @app.on_message(filters.command(['/me', 'Мой профиль'], [""]) & filters.text)
    async def answer(_, message):
        
        if message.chat.type == ChatType.PRIVATE:
            if not await check_sub(message):
                return
        
        sent = await message.reply('😎')
        commands.me += 1
        
        user_state = await add_to_net(message.from_user.id)
        _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {message.from_user.id}")
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        
        country = get_country_emojie(user_state[0][3])
        if not country:
            country = '🌏'
        
        keyboard = [
            [InlineKeyboardButton('🔎 Проверить себя', callback_data=f'check {message.from_user.id}')],
            [InlineKeyboardButton('📣 Установить канал', callback_data='channel')],
            [InlineKeyboardButton(f'{country} Установить страну', callback_data='set country')],
            [InlineKeyboardButton('❓ Как пользоваться ботом', callback_data='howto')],
        ]
        
        if _fetchall_mms or _fetchall_admins:
            keyboard.append([InlineKeyboardButton("⭐ СКВАД ГАЗДА ⭐", callback_data='squad')])
        
        keyboard.append([InlineKeyboardButton("🌴 Наш Чат Общения", url='https://t.me/+goO620eaHQo0NjMy')])
        
        await sent.edit(f'ℹ️ {message.from_user.mention}, используйте кнопки ниже для навигации\n\n'
                        f'🔥 Скаммеров слито: {user_state[0][8]}\n'
                        f'🔎 Вас искали {user_state[0][1]} раз',
                        reply_markup=InlineKeyboardMarkup(keyboard))
        
        return
    
    
    # @app.on_message(filters.command(['scam', 'скам'], ["/", "!", "$", ".", ","]) & filters.text)
    # async def answer(_, message):
    #
    #     if adm_limits.get(str(message.from_user.id)) and adm_limits[str(message.from_user.id)] + 15 >= time.time():
    #         await message.reply(
    #             f'<b>❌ Подождите {round((adm_limits[str(message.from_user.id)] + 15) - time.time())} секунд</b>',
    #             reply_markup=HIDE_KB)
    #         return
    #
    #     _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
    #     msg = message.text.split(" ", 2)
    #
    #     if (_fetchall_admins != [] and _fetchall_admins[0][2] > 0) or message.from_user.id == 1032156461:
    #
    #         if 2 > len(msg):
    #             await message.reply("<pre>/scam 🆔 Описание</pre>", reply_markup=HIDE_KB)
    #         else:
    #
    #             adm_limits[str(message.from_user.id)] = time.time()
    #
    #             msg[1] = get_user_id(msg[1])
    #
    #             _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {msg[1]}")
    #             if _fetchall_mms:
    #                 account = await app.get_users(msg[1])
    #                 await message.reply(f"🤔 {account.mention} [{msg[1]}] является гарантом нашей базы!",
    #                                     reply_markup=HIDE_KB)
    #                 return
    #
    #             try:
    #
    #                 _fetchall_scammers = sql_select(f"SELECT * FROM scammers WHERE id = {msg[1]}")
    #
    #                 if not _fetchall_scammers:
    #
    #                     try:
    #
    #                         sql_edit(f'INSERT INTO scammers VALUES(?, ?, ?, ?);',
    #                                  (msg[1], 0, 'Under Review', msg[2]))
    #
    #                         await message.reply(
    #                             '🤔 Выберите репутацию',
    #                             reply_markup=InlineKeyboardMarkup([
    #                                 [InlineKeyboardButton(
    #                                     'Плохая Репутация ⚠',
    #                                     callback_data=f'reputation 0 {msg[1]} {message.from_user.id}')],
    #                                 [InlineKeyboardButton(
    #                                     'Возможно Скаммер ⚠',
    #                                     callback_data=f'reputation 1 {msg[1]} {message.from_user.id}')],
    #                                 [InlineKeyboardButton(
    #                                     'СКАММЕР ⚠',
    #                                     callback_data=f'reputation 2 {msg[1]} {message.from_user.id}')],
    #                                 [InlineKeyboardButton(
    #                                     'Петух 🐓',
    #                                     callback_data=f'reputation 3 {msg[1]} {message.from_user.id}')],
    #                             ]))
    #
    #                     except Exception as exc:
    #                         await message.reply(exc)
    #                         await app.send_message(DIMA, f'🦍 Ошибка из /scam: {exc}')
    #                         connection.rollback()
    #
    #
    #                 else:
    #                     keyboard = [
    #                         [InlineKeyboardButton('Изменить репутацию 🔁',
    #                                               callback_data=f'change {msg[1]} {message.from_user.id}')],
    #                         [InlineKeyboardButton('Дополнить описание ➕',
    #                                               callback_data='in_dev')]
    #                     ]
    #
    #                     await message.reply(f"🤔 Пользователь с ID {msg[1]} уже занесён в нашу базу данных!\n\n"
    #                                         f"💙 <b>Репутация</b>: {_fetchall_scammers[0][2]}"
    #                                         f"\n\n📚 <b>Описание</b>: <code>{_fetchall_scammers[0][3]}</code>",
    #                                         reply_markup=InlineKeyboardMarkup(keyboard))
    #
    #             except Exception as e:
    #                 await message.reply(
    #                     e, reply_markup=HIDE_KB
    #                 )
    #     elif _fetchall_admins[0][2] == 0:
    #
    #         tutor = sql_select(f'SELECT * FROM admins WHERE intern = {message.from_user.id}')
    #
    #         if tutor:
    #
    #             msg[1] = get_user_id(msg[1])
    #
    #             await message.reply(
    #                 '🤔 Выберите репутацию',
    #                 reply_markup=InlineKeyboardMarkup([
    #                     [InlineKeyboardButton(
    #                         'Плохая Репутация ⚠',
    #                         callback_data=f'tutor 0 {msg[1]} {message.from_user.id}')],
    #                     [InlineKeyboardButton(
    #                         'Возможно Скаммер ⚠',
    #                         callback_data=f'tutor 1 {msg[1]} {message.from_user.id}')],
    #                     [InlineKeyboardButton(
    #                         'СКАММЕР ⚠',
    #                         callback_data=f'tutor 2 {msg[1]} {message.from_user.id}')],
    #                     [InlineKeyboardButton(
    #                         'Петух 🐓',
    #                         callback_data=f'tutor 3 {msg[1]} {message.from_user.id}')],
    #                 ]))
    #         else:
    #             await message.reply("⛔ <b>У вас нет куратора!</b> Напишите @Anya_its_here", reply_markup=HIDE_KB)
    #     else:
    #         await message.reply("⛔ <b>Только админы могут использовать эту команду!</b>", reply_markup=HIDE_KB)
    
    @app.on_message(filters.command(['scam', 'скам'], ["/", "!", "$", ".",]) & filters.text)
    async def answer(_, message):
        
        try:
            if adm_limits[str(message.from_user.id)] + 15 >= time.time():
                await message.reply(
                    f'<b>❌ Подождите {round((adm_limits[str(message.from_user.id)] + 15) - time.time())} секунд</b>',
                    reply_markup=HIDE_KB)
                return
        except Exception:
            pass
        
        adm_limits[str(message.from_user.id)] = time.time()
        
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        
        if (_fetchall_admins and _fetchall_admins[0][2] > 0) or message.from_user.id == 1032156461:
            msg = message.text.split(" ", 2)
            
            if 2 > len(msg):
                await message.reply("👀 Введите <code>/scam (ID | @юзер) (Описание)</code>", reply_markup=HIDE_KB)
                
            else:
                
                try:
                    account = await app.get_users(msg[1])
                    msg[1] = account.id
                    
                except Exception as e:
                    account = None
                    pass
                
                _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {msg[1]}")
                
                if _fetchall_mms:
                    if account:
                        await message.reply(f"🤔 {account.mention} [{msg[1]}] является гарантом нашей базы!",
                                            reply_markup=HIDE_KB)
                    else:
                        await message.reply(f"🤔 Этот человек [{msg[1]}] является гарантом нашей базы!",
                                            reply_markup=HIDE_KB)
                    return
                
                try:
                    
                    _fetchall_scammers = sql_select(f"SELECT * FROM scammers WHERE id = {msg[1]}")
                    
                    if not _fetchall_scammers:
                        
                        try:
                            
                            sql_edit(f'INSERT INTO scammers VALUES(?, ?, ?, ?);',
                                     (msg[1], 0, 'На рассмотрении', msg[2]))
                            
                            await message.reply(
                                '🤔 Выберите репутацию',
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton('Плохая Репутация ⚠', callback_data=f'reputation 0 '
                                                                                              f'{msg[1]} '
                                                                                              f'{message.from_user.id}')],
                                    [InlineKeyboardButton('Возможно Скаммер ⚠', callback_data=f'reputation 1 '
                                                                                              f'{msg[1]} '
                                                                                              f'{message.from_user.id}')],
                                    [InlineKeyboardButton('СКАММЕР ⚠', callback_data=f'reputation 2 '
                                                                                     f'{msg[1]} '
                                                                                     f'{message.from_user.id}')],
                                    [InlineKeyboardButton('Петух 🐓', callback_data=f'reputation 3 '
                                                                                   f'{msg[1]} '
                                                                                   f'{message.from_user.id}')],]))
                        
                        except Exception as exc:
                            await message.reply(exc)
                            connection.rollback()
                    
                    
                    else:
                        
                        keyboard = [
                            [InlineKeyboardButton(f'🔁 {_fetchall_scammers[0][2]}',
                                                  callback_data=f'change_reputation {msg[1]} {message.from_user.id}')],
                            [InlineKeyboardButton('Дополнить описание ➕', callback_data='in_dev')],
                            [InlineKeyboardButton(text='Вынести из базы ❌', callback_data=f'del {msg[1]}')],
                        ]
                        
                        if account:
                            mention = account.mention
                        else:
                            mention = 'Этот человек'
                            
                        await message.reply(f"🤔 {mention} [{msg[1]}] уже занесён в нашу базу данных!\n\n"
                                            f"💙 <b>Репутация</b>: {_fetchall_scammers[0][2]}\n\n"
                                            f"📚 <b>Описание</b>: {_fetchall_scammers[0][3]}",
                                            reply_markup=InlineKeyboardMarkup(keyboard))
                
                except Exception as e:
                    await message.reply(
                        e, reply_markup=HIDE_KB)
                    
        else:
            await message.reply("⛔ <b>Команда доступна только админам!</b>", reply_markup=HIDE_KB)
    

    @app.on_message(filters.command('Наша команда', [""]) & filters.text)
    async def answer(_, message):
        await app.send_photo(message.chat.id,
                             'https://telegra.ph/file/6ec8117345625474c8d21.png',
                             '💪 Используя кнопки ниже вы можете познакомиться с нашей командой',
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton('🌸 АДМИНЫ 🌸', callback_data='admins')],
                                 [InlineKeyboardButton('🐇 ГАРАНТЫ 🐇', callback_data='mms')]]))
    
    
    @app.on_message(filters.command('понизить', [""]) & filters.text)
    async def answer(_, message):
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (
                message.reply_to_message and message.reply_to_message.from_user.id and
                message.from_user.id == 1032156461) or (message.reply_to_message and _fetchall_admins[0][2] == 3):
            try:
                
                sql_edit(f'UPDATE admins SET status=status-1 WHERE id = {message.reply_to_message.from_user.id};', ())
                connection.commit()
                
                posted_message = await app.send_message(-1001652069822, f'''
{message.from_user.mention} понизил {message.reply_to_message.from_user.mention}

#понижение''')
                await message.reply(
                    f'<b>🐖🐖 Тудооооо</b>\n\nℹ️ https://t.me/c/{str(posted_message.chat.id)[3:]}/{posted_message.id}')
            
            except Exception as exc:
                await app.send_message(DIMA, f'🦍 Ошибка при понижении: {exc}')
                connection.rollback()
        else:
            await message.reply('⛔ Команда работает только реплаем и только для владельца и президентов.',
                                reply_markup=HIDE_KB)
    
    
    @app.on_message(filters.command('повысить', [""]) & filters.text)
    async def answer(_, message):
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (
                message.reply_to_message and message.reply_to_message.from_user.id
                and message.from_user.id == 1032156461) or (message.reply_to_message and _fetchall_admins[0][2] == 3):
            try:
                
                sql_edit(f'UPDATE admins SET status=status+1 WHERE id = {message.reply_to_message.from_user.id};', ())
                connection.commit()
                
                posted_message = await app.send_message(-1001652069822, f'''

{message.from_user.mention} повысил {message.reply_to_message.from_user.mention}

#повышение''')
                await message.reply(
                    f'<b>🐵🐵🙉 Сюдоооо</b>\n\nℹ️ https://t.me/c/{str(posted_message.chat.id)[3:]}/{posted_message.id}')
            
            except Exception as exc:
                await app.send_message(DIMA, f'🦍 Ошибка при повышении: {exc}')
                connection.rollback()
        else:
            await message.reply('⛔ Команда работает только реплаем и только для владельца и президентов.',
                                reply_markup=HIDE_KB)
    
    
    @app.on_message(filters.command('выговор', ["+"]) & filters.text)
    async def answer(_, message):
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (
                message.reply_to_message and message.reply_to_message.from_user.id and
                message.from_user.id == 1032156461) or (message.reply_to_message and _fetchall_admins[0][2] > 1):
            try:
                
                sql_edit(f'UPDATE admins SET warns=warns+1 WHERE id = {message.reply_to_message.from_user.id};', ())
                connection.commit()
                
                posted_message = await app.send_message(-1001652069822, f'''

{message.from_user.mention} дал выговор {message.reply_to_message.from_user.mention}

#выговор''')
                await message.reply(
                    f'<b>🦅🦅🦅 Тудооооао</b>\n\nℹ️ https://t.me/c/{str(posted_message.chat.id)[3:]}/{posted_message.id}')
            
            except Exception as exc:
                await app.send_message(DIMA, f'🦍 Ошибка при выговоре: {exc}')
                connection.rollback()
        else:
            await message.reply('⛔ Команда работает только реплаем и только для владельца и президентов.',
                                reply_markup=HIDE_KB)
    
    
    @app.on_message(filters.command('спасибо', ["+"]) & filters.text)
    async def answer(_, message):
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (
                message.reply_to_message and message.reply_to_message.from_user.id and
                message.from_user.id == 1032156461) or (message.reply_to_message and _fetchall_admins):
            
            try:
                
                user_state = await add_to_net(message.reply_to_message.from_user.id)
                sql_edit(f'UPDATE net SET contribution=contribution+1 '
                         f'WHERE id = {message.reply_to_message.from_user.id};', ())
                connection.commit()
                
                await message.reply(
                    f'🥰 {message.reply_to_message.from_user.mention}, <b>спасибо</b>, '
                    f'что боретесь со скамом вместе с нами.\n\n🔥 Вы слили уже {user_state[0][8] + 1} скаммеров, '
                    f'так держать!')
            
            except Exception as exc:
                await app.send_message(DIMA, f'🦍 Ошибка при +спасибо: {exc}')
                connection.rollback()
        else:
            await message.reply('⛔ Команда работает только реплаем и только для админов.',
                                reply_markup=HIDE_KB)
    
    
    @app.on_message(filters.command('выговор', ["-"]) & filters.text)
    async def answer(_, message):
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (message.reply_to_message and message.reply_to_message.from_user.id and message.from_user.id == 1032156461) \
                or (message.reply_to_message and _fetchall_admins[0][2] > 1):
            try:
                
                sql_edit(f'UPDATE admins SET warns=warns-1 WHERE id = {message.reply_to_message.from_user.id};', ())
                connection.commit()
                
                posted_message = await app.send_message(-1001652069822, f'''

{message.from_user.mention} снял выговор {message.reply_to_message.from_user.mention}

#выговор

    ''')
                await message.reply(
                    f'<b>🦛🦛 Сюдооооо</b>\n\nℹ️ https://t.me/c/{str(posted_message.chat.id)[3:]}/{posted_message.id}')
            
            except Exception as exc:
                await app.send_message(DIMA, f'🦍 Ошибка при снятии выговора: {exc}')
                connection.rollback()
        else:
            await message.reply('⛔ Команда работает только реплаем и только для владельца и президентов.',
                                reply_markup=HIDE_KB)
    
    
    @app.on_message(filters.command('unmm', ["/"]) & filters.text)
    async def answer(_, message):
        
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (message.from_user.id == 1032156461) or (_fetchall_admins[0][2] == 3):
            msg = message.text.split()
            
            if len(msg) > 1:
            
                try:
                    # msg[1] - ID, msg[2] - Cause
                    
                    _fetchall_scammers = sql_select(f"SELECT * FROM mms WHERE id = {msg[1]}")
                    if _fetchall_scammers:  # ['/add_scammer', ID (int), Cause (str)]
                        
                        sql_edit(f'DELETE FROM mms WHERE id = {msg[1]}', ())
                        posted_message = await app.send_message(-1001652069822, f'''

Админ {message.from_user.mention} удалил человека из ГАРАНТОВ базы!
#id{message.from_user.id} #удаление_из_бд
=============
Данные о пользователе:

<b>🆔 ID</b>: <code>{msg[1]}</code> <a href=tg://openmessage?user_id={msg[1]}>Вечная Ссылка</a>

                                        ''')
                        await message.reply(
                            f'<b>👋 | Успешно удалил пользователя из гарантов базы.'
                            f'(ЧО ЗА ЛОХ ХАХАХАХ)</b>\n\nℹ️ {posted_message.link}')
                    
                    else:
                        await message.reply(f"Пользователя с ID {msg[1]} нет в гарантах базы", reply_markup=HIDE_KB)
                except Exception as e:
                    
                    await message.reply(
                        "Введите /unmm (ID пользователя/@юзернейм)", reply_markup=HIDE_KB
                    )
                    await message.reply(
                        e, reply_markup=HIDE_KB
                    )
            else:
                await message.reply("Не указан 🆔", reply_markup=HIDE_KB)
        else:
            await message.reply("⛔ Только владелец и президент могут использовать эту команду!", reply_markup=HIDE_KB)
            return
        
    
    @app.on_message(filters.command('unadmin', ["/"]) & filters.text)
    async def answer(_, message):
        
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (message.from_user.id == 1032156461) or (_fetchall_admins[0][2] == 3):
            msg = message.text.split()
            
            if len(msg) > 1:
            
                try:
                    # msg[1] - ID, msg[2] - Cause
                    
                    _fetchall_scammers = sql_select(f"SELECT * FROM admins WHERE id = {msg[1]}")
                    if _fetchall_scammers:  # ['/add_scammer', ID (int), Cause (str)]
                        
                        sql_edit(f'DELETE FROM admins WHERE id = {msg[1]}', ())
                        
                        try:
                            await app.send_message(msg[1], '👀 Ваша репутация в базе была изменена',
                                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                       text='Чекнуть себя 🔎',
                                                       callback_data=f'check {msg[1]}'
                                                   )]]))
                            commands.changed += 1
                            
                        except Exception as e:
                            await app.send_message(DIMA, f'⛔ Не получилось отправить уведомление!\n\n<pre>{e}</pre>')
                        
                        posted_message = await app.send_message(-1001652069822, f'''
    
Админ {message.from_user.mention} удалил человека из АДМИНОВ базы!
#id{message.from_user.id} #удаление_из_бд
=============
Данные о пользователе:

<b>🆔 ID</b>: <code>{msg[1]}</code> <a href=tg://openmessage?user_id={msg[1]}>Вечная Ссылка</a>
    
                                            ''')
                        await message.reply(
                            f'<b>👋 | Успешно удалил пользователя из админов базы. (ЧО ЗА ЛОХ ХАХАХАХ)</b>\n\n'
                            f'ℹ️ https://t.me/c/{str(posted_message.chat.id)[3:]}/{posted_message.id}')
                    
                    else:
                        await message.reply(f"Пользователя с ID {msg[1]} нет в админах базы", reply_markup=HIDE_KB)
                except Exception as e:
                    await message.reply(
                        "Введите /unadmin (ID пользователя/@юзернейм)", reply_markup=HIDE_KB
                    )
                    await message.reply(
                        e, reply_markup=HIDE_KB
                    )
            else:
                await message.reply("Не указан 🆔!", reply_markup=HIDE_KB)
            
        else:
            await message.reply("⛔ Только владелец и президенты могут использовать эту команду!", reply_markup=HIDE_KB)
            return
    
    
    @app.on_message(filters.command('#рассылка_мидлам', [""]) & filters.text)
    async def answer(_, message):
        if message.from_user.id == 1032156461:
            mms = sql_select(f"SELECT * FROM mms")
            
            await message.reply('Рассылка запущена!', reply_markup=HIDE_KB)
            counter = 0
            
            for mm in mms:
                try:
                    await app.send_message(mm[0], message.text, reply_markup=HIDE_KB)
                    counter += 1
                except Exception as e:
                    await message.reply(
                        f'Error while trying to send message\n\nID - <code>{mm[0]}</code>\n\nReason - {e}')
            
            await message.reply(f'Рассылка успешно окончена! \n\n Успешно доставлено {counter} сообщений!')
    
    
    @app.on_message(filters.command('dm', ["/"]) & filters.text)
    async def answer(_, message):
        
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (message.from_user.id == 1032156461) or (_fetchall_admins[0][2] == 3):
            msg = message.text.split(' ', 2)
            try:
                await app.send_message(chat_id=msg[1], text=f'''
<b>🆕 Сообщение от администрации:</b>

<i>{msg[2]}</i>
                ''')
            except Exception as e:
                await message.reply(f'{e}')
    
    
    @app.on_message(filters.command('admin', ["/"]) & filters.text)
    async def answer(_, message):
        
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (message.from_user.id == 1032156461) or (_fetchall_admins[0][2] == 3):
            msg = message.text.split()
            
            if 2 > len(msg):
                await message.reply(
                    "<q>Введите /admin 🆔</q>", reply_markup=HIDE_KB)
                return
            
            msg[1] = await get_user_id(msg[1])
            
            try:
                
                _fetchall_admins = sql_select(f"SELECT id FROM admins WHERE id = {msg[1]}")
                if not _fetchall_admins:
                    
                    sql_edit(f'INSERT INTO admins VALUES(?, ?, ?, ?);', (msg[1], 0, 0, 0))
                    await message.reply('✅')
                
                else:
                    await message.reply(f"Пользователь с ID {msg[1]} уже админ!", reply_markup=HIDE_KB)
            except Exception as e:
                
                await message.reply(
                    f"Что-то пошло не так\n\n<pre>{e}</pre>", reply_markup=HIDE_KB)
        else:
            await message.reply(
                "⛔ Только владелец и президенты могут использовать эту команду!", reply_markup=HIDE_KB)
            return
    
    
    @app.on_message(filters.command('trust', ["/", "!"]) & filters.text)
    async def answer(_, message):
        
        _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {message.from_user.id}")
        if (message.from_user.id == 1032156461) or _fetchall_mms:
            
            msg = message.text.split()
            if 2 > len(msg):
                await message.reply("<q>Введите /trust 🆔</q>", reply_markup=HIDE_KB)
                return
            
            msg[1] = await get_user_id(msg[1])
            
            try:
                _fetchall_net = sql_select(f"SELECT is_trusted FROM net WHERE id = {msg[1]}")
                if _fetchall_net and _fetchall_net[0][0] == 0:
                    
                    sql_edit(f'UPDATE net SET is_trusted= ? WHERE id = ?;', (message.from_user.id, msg[1]))
                    posted_message = await app.send_message(
                        -1001652069822,
                        f'''
Гарант {message.from_user.mention} назначил себе нового проверенного!
#id{message.from_user.id} #NewTrusted
=============
Данные о пользователе:

<b>🆔 ID</b>: <code>{msg[1]}</code> <a href=tg://openmessage?user_id={msg[1]}>Вечная Ссылка</a>''')
                    await message.reply('✅')
                    await message.reply(
                        f'<b>👋 | Вы успешно назначили {(await app.get_users(msg[1])).mention} проверенным'
                        f'\n\nℹ️ {posted_message.link}')
                
                else:
                    await message.reply(f"Пользователь {(await app.get_users(msg[1])).mention} "
                                        f"уже проверенный {(await app.get_users(_fetchall_net[0][0])).mention}!",
                                        reply_markup=HIDE_KB)
            except Exception as e:
                
                await message.reply(
                    "<q>Введите /trust 🆔</q>", reply_markup=HIDE_KB
                )
                await message.reply(
                    e, reply_markup=HIDE_KB
                )
        else:
            await message.reply("⭐ Доступно только гарантам!", reply_markup=HIDE_KB)
    
    
    @app.on_message(filters.command('untrust', ["/", "!"]) & filters.text)
    async def answer(_, message):
        
        _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {message.from_user.id}")
        if message.from_user.id == 1032156461 or _fetchall_mms:
            msg = message.text.split()
            
            if 2 > len(msg):
                await message.reply("<q>Введите /trust 🆔</q>", reply_markup=HIDE_KB)
                return
            
            msg[1] = await get_user_id(msg[1])
            
            try:
                # msg[1] - ID, msg[2] - Cause
                
                _fetchall_net = sql_select(f"SELECT is_trusted FROM net WHERE id = {msg[1]}")
                if _fetchall_net and _fetchall_net[0][0] == message.from_user.id or message.from_user.id == 1032156461:
                    
                    sql_edit(f'UPDATE net SET is_trusted=0 WHERE id = {msg[1]}', ())
                    posted_message = await app.send_message(-1001652069822, f'''
Гарант {message.from_user.mention} удалил человека из проверенных!
#id{message.from_user.id} #TrustedBeingRemoved
=============
Данные о пользователе:

<b>🆔 ID</b>: <code>{msg[1]}</code> <a href=tg://openmessage?user_id={msg[1]}>Вечная Ссылка</a>''')
                    await message.reply('✅')
                    await message.reply(
                        f'<b>👋 | Успешно удалил пользователя из ваших проверенных.'
                        f'(ИЗИ МАМОНТ БОЖЕ)</b>\n\nℹ️ {posted_message.link}')
                
                else:
                    await message.reply(f"🍑 Пользователя с ID {msg[1]} нет в списке ващих проверенных",
                                        reply_markup=HIDE_KB)
            except Exception as e:
                
                await message.reply("<q>Введите /untrust 🆔</q>", reply_markup=HIDE_KB)
                await message.reply(e, reply_markup=HIDE_KB)
        else:
            await message.reply("⭐ Доступно только гарантам!", reply_markup=HIDE_KB)


    @app.on_message(filters.command('settings', ["/"]) & filters.text)
    async def answer(_, message):
        
        await check_if_a_user(message)
        
        if message.chat.type == ChatType.GROUP or message.chat.type == ChatType.SUPERGROUP:
            
            status = await app.get_chat_member(chat_id=message.chat.id,
                                               user_id=message.from_user.id)
            
            if status.status == ChatMemberStatus.ADMINISTRATOR or status.status == ChatMemberStatus.OWNER \
                    or message.from_user.id == 1032156461:
                
                group = sql_select(f"SELECT * FROM groups WHERE id = {message.chat.id}")[0]
                
                if group[2] == -1:
                    autoban = '❌ Автобан отключён'
                elif group[2] == 0:
                    autoban = '✅ Плохая репутация +'
                elif group[2] == 1:
                    autoban = '✅ Возможно Скаммер +'
                elif group[2] == 2:
                    autoban = '✅ Банить только Скаммеров'
                else:
                    autoban = '❓ Неизвестная ошибка'
                
                if group[3] == 1:
                    enabledalert = '✅'
                else:
                    enabledalert = '❌'
                
                if group[4] == 1:
                    enabledhelp = '✅'
                else:
                    enabledhelp = '❌'
                
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(f"АВТОБАН - ({autoban}) ✅",
                                           callback_data=f'autoban {message.chat.id}')],
                     [InlineKeyboardButton(f"{enabledalert} ПРЕДУПРЕЖДЕНИЯ",
                                           callback_data=f'scamwarn {message.chat.id}')],
                     [InlineKeyboardButton(f"{enabledhelp} СЛИТЬ СКАМЕРА",
                                           callback_data=f'slivscam {message.chat.id}')]]
                )
                
                await message.reply(
                    'Первая кнопка отвечает за автобан. '
                    'Вы можете выбрать, начиная с какой репутации пользователь будет забанен.\n\n'
                    'Вторая кнопка отвечает за сообщения о том, что человек скам, если он пишет в чат.\n\n'
                    'Третья кнопка отвечает за предложение слить скаммера в нашем официальном чате.\n\n\n'
                    '<b>Настройки группы:</b>',
                    reply_markup=keyboard)
            
            else:
                await message.reply('⛔ Вы не админ в этой группе!', reply_markup=HIDE_KB)
        
        else:
            await message.reply('⛔ Эта команда предназначена только для групп!', reply_markup=HIDE_KB)
    
    
    @app.on_message(filters.command('Провести сделку 💰', "") & filters.text)
    async def answer(_, message):
        
        if message.chat.type == ChatType.PRIVATE:
            await message.reply(
                '<a href=https://telegra.ph/file/952f65f85ddf10d64b4a5.png>\u200B</a>'
                '<b>🌴 Вы можете провести безопасную сделку через нашего бота</b>\n\n'
                '👩‍💻 Бот автоматически создаст группу для сделки и подберёт вам гаранта из нашей базы.',
                # ' <b>Гаранты берут оплату - 10% от суммы сделки</b>'
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton('Открыть сделку 🌴', callback_data='trade')],
                     [InlineKeyboardButton('Скрыть', callback_data='hide')]]))
        
        else:
            await message.reply('⚠️ Данный функционал работает только в личке с ботом',
                                reply_markup=InlineKeyboardMarkup(
                                    [[InlineKeyboardButton('Перейти ➡️', callback_data='dms')]]))
    
    @app.on_message(filters.command('mm', ["/"]) & filters.text)
    async def answer(_, message):
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        if (message.from_user.id == 1032156461) or (_fetchall_admins[0][2] == 3):
            msg = message.text.split()
            
            if 2 > len(msg):
                await message.reply(
                    "Введите <code>/mm (ID пользователя)</code>", reply_markup=HIDE_KB)
                
                return
            
            msg[1] = await get_user_id(msg[1])
            
            try:
                
                _fetchall_admins = sql_select(f"SELECT * FROM mms WHERE id = {msg[1]}")
                if not _fetchall_admins:  # ['/add_scammer', ID (int), Cause (str)]
                    sql_edit(f'INSERT INTO mms VALUES(?, ?, ?, ?, ?, ?);',
                             (msg[1], 0, 0, 0, 0, 0))
                
                try:
                    await app.send_message(msg[1], '👀 Ваша репутация в базе была изменена',
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                               text='Чекнуть себя 🔎',
                                               callback_data=f'check {msg[1]}'
                                           )]]))
                    commands.changed += 1
                
                except Exception as e:
                    await app.send_message(DIMA,
                                           f'⛔ Не получилось отправить уведомление!\n\n<pre>{e}</pre>')
                
                
                else:
                    await message.reply(f"Пользователь с ID {msg[1]} уже гарант!", reply_markup=HIDE_KB)
            except Exception as e:
                
                await message.reply(
                    "<quote>Введите  /mm 🆔</quote>", reply_markup=HIDE_KB
                )
                await message.reply(
                    e, reply_markup=HIDE_KB
                )
        else:
            await message.reply(
                "⛔ Только владелец и президенты могут использовать эту команду!", reply_markup=HIDE_KB
            )
            return
    
    
    @app.on_message(filters.group)
    async def is_a_scammer_warn(_, message):
        
        if message.chat.id == -1001740473921:
            if message.text and '!админ' in message.text.lower():
                await message.reply('✅ Я позвал админов!', reply_markup=HIDE_KB)
                await app.send_message(
                    chat_id=-1001869548358,
                    text='🔥 <b>Админы, вас зовут в чат жалоб</b>',
                    reply_markup=CHANNEL_KB)
        
        if message.text and 'что делать' in message.text.lower():
            await message.reply('Что делать, если ...', reply_markup=WHAT_TO_DO_KB)
        
        _fetchall_scammers = sql_select(f"SELECT * FROM scammers WHERE id = {message.from_user.id}")
        
        if _fetchall_scammers:
            group = sql_select(f"SELECT * FROM groups WHERE id = {message.chat.id}")[0]
            if group and group[3] == 1:
                commands.scamwarn += 1
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('РАЗВЕРНУТЬ 🙈',
                                                                       callback_data=f'alert+ {message.from_user.id}')],
                                                 [InlineKeyboardButton('ЗАБАНИТЬ ⛔',
                                                                       callback_data=f'ban {message.from_user.id}')]])
                
                await message.reply(
                    f'''
<a href={random.choice(scam_pictures)}>\u200B</a>
⚠️ {message.from_user.mention} [<code>{message.from_user.id}</code>] находится в нашей базе. Будьте осторожны!

💙 <b>Репутация</b>: {_fetchall_scammers[0][2]}''', reply_markup=keyboard)
            
            if group and group[2] >= 0:
                
                reputation = False
                if _fetchall_scammers[0][2].startswith('СКАММЕР'):
                    reputation = 2
                elif _fetchall_scammers[0][2].startswith('Потенциальный Скаммер') \
                        or _fetchall_scammers[0][2].startswith('Возможно Скаммер'):
                    reputation = 1
                elif _fetchall_scammers[0][2].startswith('Плохая Репутация'):
                    reputation = 0
                
                if reputation and group[2] <= reputation:
                    await app.ban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
                    await message.reply('✅ Скаммер был автоматически забанен', reply_markup=HIDE_KB)
    
    
    @app.on_message(filters.command('Слить скаммера 😡', ''), group=2)
    async def have_you_been_scammed(_, message):
        
        if message.chat.type == ChatType.PRIVATE:
            await message.reply(
                '<a href=https://telegra.ph/file/d9f3c88c3f0e36f89bb17.png>\u200B</a>'
                '<b>😮‍💨 Если вы стали жертвой мошенников - жмите кнопку "Написать жалобу"</b>\n\n'
                '👩‍💻 Вы будете направлены в чат с нашими волонтёрами, они разберутся в ситуации и '
                'занесут мошенника в базу. Это бесплатно',
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton('Написать жалобу 📝', callback_data='delation')],
                     [InlineKeyboardButton('Скрыть', callback_data='hide')]]))
        
        else:
            await message.reply('⚠️ Данный функционал работает только в личке с ботом',
                                reply_markup=InlineKeyboardMarkup(
                                    [[InlineKeyboardButton('Перейти ➡️', callback_data='dms')]]))
    
    
    @app.on_message(filters.group & filters.text, group=2)
    async def have_you_been_scammed(_, message):
        
        commands.report += 1
        
        if message.chat.id == -1001740473921 and 'слить скаммера' in message.text.lower():
            await message.reply('Как слить скаммера написано в этом посте - https://t.me/AntiScamRoblox/307',
                                reply_markup=HIDE_KB)
        
        if message.text.startswith('/'):
            return
        
        try:
            for word in scam_list:
                if message.text and word in message.text.lower():
                    group = sql_select(f"SELECT * FROM groups WHERE id = {message.chat.id}")[0]
                    if group and group[4] == 1:
                        our_group = await app.get_chat(report_group)
                        await message.reply(f'''
<b>🤬 ВАС СКАМНУЛИ? ХОТИТЕ СЛИТЬ ОБМАНЩИКА?</b>

СРОЧНО!!! Скидывайте пруфы в @{our_group.username} и мы занесём скаммера в базу
            ''', reply_markup=AS_REPORT_KB)
                        return
        except FloodWait:
            pass
        
        except Exception as e:
            await app.send_message(DIMA,
                                   f'⛔ Не получилось отправить промпт жалобы в группу!\n\n<pre>{e}</pre>')
            return
    
    
    @app.on_message(filters.chat(-1001949170455), group=3)
    async def clear(_, message):
        _paterpervsgiee = sql_select(
            f"SELECT initiator FROM delations "
            f"WHERE topic_id = {message.reply_to_message_id} AND initiator = {message.from_user.id}")
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {message.from_user.id}")
        
        if not _fetchall_admins and not _paterpervsgiee:
            await app.delete_messages(message.chat.id, message.id)
        
    
    
    @app.on_message(filters.sticker, group=31)
    async def clean(_, message):
        if message.sticker.set_name in bad_stickers:
            await app.delete_messages(message.chat.id, message.id)
    
    
    @app.on_message(filters.new_chat_members, group=30)
    async def hello(_, message):
        
        sent = await app.send_message(message.chat.id, f'<b>👋 Добро пожаловать, {message.from_user.mention}!</b>')
        kb = InlineKeyboardMarkup([[InlineKeyboardButton('🤝', callback_data='privet')]])
        person = message.from_user
        
        user_state = await add_to_net(message.from_user.id)
        _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {person.id}")
        _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {person.id}")
        _fetchall_scammers = sql_select(f"SELECT * FROM scammers WHERE id = {person.id}")
        
        
        
        if _fetchall_mms:
            text = f'<a href={themes["default"]["mm"]}>\u200B</a>\n' \
                   '🔥 <i>К чату присоединился <b>Гарант</b> GASD</i>'
        
        elif user_state[0][6] > 0:
            text = f'<a href={themes["default"]["trusted"]}>\u200B</a>\n' \
                   f'🔥 <i>К чату присоединился <b>человек, проверенный гарантом</b> GASD</i>'
        
        elif _fetchall_admins:
            
            if person.id == 1032156461:
                role = '🔥 Создатель'
            elif _fetchall_admins[0][2] == 0:
                role = 'Стажёр'
            elif _fetchall_admins[0][2] == 1:
                role = 'Админ'
            elif _fetchall_admins[0][2] == 2:
                role = 'Директор'
            elif _fetchall_admins[0][2] == 3:
                role = 'Президент'
            else:
                role = 'долбоёб из'
            
            text = f'<a href={themes["default"]["staff"]}>\u200B</a>\n' \
                   f'🔥 <i>К чату присоединился <b>{role}</b> GASD</i>'
        
        elif _fetchall_scammers:
            
            if _fetchall_scammers[0][2] == 'СКАММЕР ⚠':
                
                text = f'<a href={themes["default"]["scam"]}>\u200B</a>\n' \
                       '⚠️ <i>К чату присоединился <b>Скаммер</b>!</i>\n\n' \
                       'Не доверяйте этому человеку.'
                kb = InlineKeyboardMarkup([[InlineKeyboardButton('ЗАБАНИТЬ ⛔',
                                                                 callback_data=f'ban {message.from_user.id}')]])
            
            
            else:
                
                scam_chance = await scam_chances(person, 70)
                
                text = (f'<a href={themes["default"]["high_scam_chances"]}>\u200B</a>\n'
                        f'⚠️ <i>К чату присоединился <b>человек с высоким шансом скама</b>!</i>\n\n'
                        f'Вероятность скама: {scam_chance}%')
                kb = InlineKeyboardMarkup([[InlineKeyboardButton('ЗАБАНИТЬ ⛔',
                                                                 callback_data=f'ban {message.from_user.id}')]])
        
        else:
            await update_stats(person)
            
            scam_chance = await scam_chances(person, 45)
            
            text = (f'<a href={themes["default"]["no_data"]}>\u200B</a>\n'
                    f'ℹ️ <i>Человека нет в базе</i>\n\n'
                    f'Вероятность скама: {scam_chance}%')
        
        await sent.reply(text=text, reply_markup=kb, quote=False)
    
    
    @app.on_message(filters.forwarded & filters.private, group=10)
    async def check_forwarded(_, message):
        commands.check += 1
        sent = await message.reply(f'⏳ {message.from_user.mention}, загружаем...\n\nℹ️ {random.choice(hints)}')
        
        if not message.forward_from:
            await sent.edit(
                'Бот не смог увидеть, от кого переслано сообщение. '
                'Возможно, пользователь скрыл свой ник при пересылке.')
            return
        
        if message.chat.type == ChatType.PRIVATE:
            if not await check_sub(message):
                return
        
        res = await check_person_by_id(message.forward_from)
        if res:
            await sent.edit(res, reply_markup=AS_REPORT_KB)
            await if_supports_gasd(message.reply_to_message.from_user, message.chat.id)
            await if_hedgehog(message.reply_to_message.from_user, message.chat.id)
    
    
    @app.on_inline_query()
    async def answer(_, inline_query):
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    title="🔥 Проверить себя на скам",
                    input_message_content=InputTextMessageContent(
                        await check_person_by_id(inline_query.from_user)
                    ),
                    description="Покажет вашу репутацию в боте",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(
                                "💙 Проверка на скам 💙",
                                url='t.me/AntiScamDatabaseBot'
                            )]
                        ]
                    )
                ),
            ],
            cache_time=1
        )
    
    
    @app.on_callback_query()
    async def react(_, callback_query):
        
        global banned
        data = callback_query.data
        
        if data.startswith('ban'):
            status = await app.get_chat_member(chat_id=callback_query.message.chat.id,
                                               user_id=callback_query.from_user.id)
            
            if status.status == ChatMemberStatus.ADMINISTRATOR or status.status == ChatMemberStatus.OWNER:
                
                try:
                    await app.ban_chat_member(chat_id=callback_query.message.chat.id, user_id=data.split()[1])
                    await callback_query.answer(
                        f"✅ Участник был успешно забанен",
                        show_alert=True)
                    commands.banned += 1
                    await app.send_message(1032156461,
                                           f'🔥 Новый бан. '
                                           f'Чат - {callback_query.message.chat.title}, '
                                           f'Инициатор - {callback_query.from_user.mention}')
                except Exception as e:
                    await callback_query.answer(
                        f"{e}",
                        show_alert=True)
            else:
                await callback_query.answer(
                    f"⛔ Доступно только админам и владельцу чата",
                    show_alert=True)
        
        elif data.startswith('dms'):
            await callback_query.answer(url='t.me/AntiscamDatabaseBot?start=callback')
        
        elif data.startswith('accept_terms'):
            
            msg = data.split()
            
            if len(msg) > 1:
            
                if callback_query.from_user.id == int(msg[1]):
                    ...
                    # scamdata = sql_select(f"SELECT * FROM scammers WHERE id = {msg[1]}")
                    # netdata = sql_select(f"SELECT * FROM scammers WHERE id = {msg[1]}")
                else:
                    await callback_query.answer('⛔ Это не Ваша кнопка')
            else:
                await callback_query.answer("⛔ Что-то пошло не так! Уже отправил ошибку создателю.", show_alert=True)
                await app.send_message(DIMA, f'⛔ Неправильный Callback у кнопки TOS!\n\n{data}')
                return
        
        elif data.startswith('Xsorry'):
            msg = data.split()
            
            if len(msg) > 1:
            
                if callback_query.from_user.id == int(msg[1]):
                    
                    scamdata = sql_select(f"SELECT * FROM scammers WHERE id = {msg[1]}")
                    netdata = sql_select(f"SELECT * FROM scammers WHERE id = {msg[1]}")
                    
                    if scamdata and netdata and netdata[0][7] == 0:
                        if scamdata[0][3].lower().startswith('поддержка скам груп') and len(scamdata[3]) < 64:
                            await callback_query.message.edit(
                                f"💁‍♂️ <b>{callback_query.from_user.mention}, ознакомьтесь с информацией ниже:</b>\n\n"
                                "Вы находитесь в базе за \"<i>Поддержку скам группировки</i>\", за что мы больше не"
                                "добавляем в базу. Это значит, что вы можете выйти из нашей базы\n\n"
                                "<b>При выходе из базы вы соглашаетесь:</b>\n\n"
                                "• Идти через гарантов базы GASD и не отказываться от них,\n"
                                "• Не распускать диз-инфу про базу GASD\n",
                                "• Не распускать диз-инфу про базу GASD\n",
                                "• Не скамить, не помогать скаммерам и не распространять скам"
                                "\n\n🎓 <b>Удалиться из базы можно только 1 раз</b>",
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                    text='Принять условия ✅',
                                    callback_data=f'accept_terms {msg[1]}'
                                )]]))
                            return
                        elif scamdata[0][3].lower().startswith('отказ от гаранта') and len(scamdata[3]) < 64:
                            await callback_query.message.edit(
                                f"💁‍♂️ <b>{callback_query.from_user.mention}, ознакомьтесь с информацией ниже:</b>\n\n"
                                "Вы находитесь в базе за \"<i>Отказ от гаранта</i>\", но у вас есть возможность "
                                "удалить себя из базы\n\n"
                                "<b>При выходе из базы вы соглашаетесь:</b>\n\n"
                                "• Идти через гарантов базы GASD и не отказываться от них,\n"
                                "• Не распускать диз-инфу про базу GASD\n",
                                "• Не распускать диз-инфу про базу GASD\n",
                                "• Не скамить, не помогать скаммерам и не распространять скам"
                                "\n\n🎓 <b>Удалиться из базы можно только 1 раз</b>",
                                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                    text='Принять условия ✅',
                                    callback_data=f'accept_terms {msg[1]}'
                                )]]))
                            return
                        else:
                            await callback_query.message.edit(
                                "⛔ Отказано. Следите за актуальной информацией на @AntiScamRoblox",
                                reply_markup=HIDE_KB
                            )
                            return
                    else:
                        await callback_query.message.edit(
                            "⛔ <b>Ошибка!</b>\n\nЛибо вы уже не в базе, либо вы уже выходили с базы.",
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                text='Чекнуть себя 🔎',
                                callback_data=f'check {msg[1]}'
                            )]])
                        )
                        return
                else:
                    await callback_query.answer('⛔ Это не Ваша кнопка')
            else:
                await callback_query.answer("⛔ Что-то пошло не так! Уже отправил ошибку создателю.", show_alert=True)
                await app.send_message(DIMA, f'⛔ Неправильный Callback у кнопки SORRY!\n\n{data}')
                return
            
        elif data.startswith('del '):
            _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {callback_query.from_user.id}")
            
            if _fetchall_admins != [] or callback_query.from_user.id == 1032156461:
                msg = data.split()
                
                if len(msg) > 1:
                
                    try:
                        person = await app.get_users(msg[1])
                        msg[1] = person.id
                    except Exception as e:
                        await app.send_message(DIMA, f'Ошибка при получении профиля\n\n<pre>{e}</pre>')
                    
                    try:
                        # msg[1] - ID, msg[2] - Cause
                        
                        _fetchall_scammers = sql_select(f"SELECT * FROM scammers WHERE id = {msg[1]}")
                        if _fetchall_scammers:  # ['/add_scammer', ID (int), Cause (str)]
                            
                            sql_edit(f'DELETE FROM scammers WHERE id = {msg[1]}', ())
                            
                            try:
                                await app.send_message(msg[1], '👀 Ваша репутация в базе была изменена',
                                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                           text='Чекнуть себя 🔎',
                                                           callback_data=f'check {msg[1]}'
                                                       )]]))
                                commands.changed += 1
                            
                            except Exception as e:
                                await app.send_message(DIMA, f'⛔ Не получилось отправить уведомление!\n\n<pre>{e}</pre>')
                            
                            posted_message = await app.send_message(-1001652069822, f'''
    
Админ {callback_query.from_user.mention} удалил человека из базы!
#id{callback_query.from_user.id} #удаление_из_бд
=============
Данные о пользователе:

<b>🆔 ID</b>: <code>{msg[1]}</code> <a href=tg://openmessage?user_id={msg[1]}>Вечная Ссылка</a>
    
                                                        ''')
                            await callback_query.message.edit(
                                f'<b>👋 | Успешно удалил '
                                f'<a href=tg://openmessage?user_id={msg[1]}>пользователя из базы.</a>'
                                f'</b>\n\nℹ️ https://t.me/c/{str(posted_message.chat.id)[3:]}/{posted_message.id}')
                        
                        else:
                            await callback_query.message.edit(f"Пользователя с ID {msg[1]} нет в нашей базе данных",
                                                              reply_markup=HIDE_KB)
                    except Exception as e:
                        
                        await callback_query.message.edit(
                            "Введите <code>/del (ID пользователя/@юзернейм)</code>", reply_markup=HIDE_KB
                        )
                        await callback_query.message.edit(
                            e, reply_markup=HIDE_KB
                        )
                else:
                    await callback_query.answer("⛔ Что-то пошло не так! Уже отправил ошибку создателю.",
                                                show_alert=True)
                    await app.send_message(DIMA, f'⛔ Неправильный Callback у кнопки DEL!\n\n{data}')
                    return
                
            else:
                await callback_query.answer("⛔ Только админы могут использовать эту команду!", show_alert=True)
                return
        
        elif data.startswith('howto'):
            commands.help += 1
            
            await app.send_chat_action(callback_query.message.chat.id, ChatAction.UPLOAD_VIDEO)
            sent = await app.send_video(
                chat_id=callback_query.message.chat.id,
                video='BAACAgIAAxkDAAEE8jlkqVpmXjQIgMTJyg-OY_6FKnWSGQAC-jMAAuQEUEn_RdEmWrw4pB4E',
                caption='''Я - GASD 💪🧬, бот, помогающий проверять людей на скам и сливать скаммеров.

/start
- <i>Перезапуск бота, если пропали кнопки</i> 🧬

/check (@юзер | ID проверяемого, без скобок)
- <i>Проверить человека на скам</i> 😳

/me
- <i>Ваш профиль</i> 👻

<b>👇 Остальной функционал доступен по кнопкам в меню</b>

Слить скаммера - @GasdReport
                    ''',
                reply_markup=DEFAULT_KB)
        
        
        elif data.startswith('mmchat'):
            await callback_query.message.edit(
                f'''
{callback_query.from_user.mention}, нажмите на кнопку, чтобы зайти в Чат Гарантов GASD</b> 🗽⚡

Бот в автоматически принимает и отклоняет заявки. Приняты могут быть только гаранты нашей базы.''',
                reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⭐ ЧАТ ГАРАНТОВ ⭐", url="https://t.me/+HVV80SR_f7QxNGEy")],
                [InlineKeyboardButton('Отмена ❌', callback_data='me')]]))
        
        elif data.startswith('adminchat'):
            await callback_query.message.edit(
                f'{callback_query.from_user.mention}, нажмите на кнопку, чтобы зайти в Чат Админов GASD</b> 🌴⚡'
                'Бот в автоматически принимает и отклоняет заявки. Приняты могут быть только волонтёры нашей базы.',
                reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⭐ ЧАТ АДМИНОВ ⭐", url="https://t.me/+_iniiZ10pPljYmZi")],
                [InlineKeyboardButton('Отмена ❌', callback_data='me')]]))
        
        
        elif data.startswith('hide'):
            
            await callback_query.answer(f"✅ Сообщение скрыто")
            await app.delete_messages(callback_query.message.chat.id, callback_query.message.id)
        
        elif data.startswith('set country'):
            
            await callback_query.message.edit(f"🌎 Выберите страну из списка ниже:",
                                              reply_markup=COUNTRIES_1)
        
        elif data.startswith('country'):
            
            user_state = sql_select(f"SELECT * FROM net WHERE id = {callback_query.from_user.id}")
            
            sql_edit(f'UPDATE net SET country=(?) WHERE id={callback_query.from_user.id}', (data.split()[1],))
            
            await callback_query.message.edit(f"✅ Страна успешно обновлена",
                                              reply_markup=InlineKeyboardMarkup(
                                                  [[InlineKeyboardButton('Мой профиль ↩️', callback_data='me')]]))
        
        elif data.startswith('change'):
            
            msg = data.split(' ', 3)
            
            if callback_query.from_user.id != int(msg[2]):
                await callback_query.answer('☺️ Это не ваша кнопка!')
                return
            
            await callback_query.answer('👇 Выберите репутацию')
            
            await callback_query.message.reply(
                '🤔 Выберите репутацию',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        'Плохая Репутация ⚠',
                        callback_data=f'reputation 0 {msg[1]} {callback_query.from_user.id}')],
                    [InlineKeyboardButton(
                        'Возможно Скаммер ⚠',
                        callback_data=f'reputation 1 {msg[1]} {callback_query.from_user.id}')],
                    [InlineKeyboardButton(
                        'СКАММЕР ⚠',
                        callback_data=f'reputation 2 {msg[1]} {callback_query.from_user.id}')],
                    [InlineKeyboardButton(
                        'Петух 🐓',
                        callback_data=f'reputation 3 {msg[1]} {callback_query.from_user.id}')],
                ]))
        
        elif data.startswith('approve'):
            
            msg = data.split(' ', 4)
            
            admin = sql_select(f'SELECT * FROM admins WHERE id = {msg[2]}')[0]
            intern = sql_select(f"SELECT * FROM admins WHERE id={msg[1]}")[0]
            
            if not admin[3]:
                sql_edit(f'UPDATE admins SET dob=(?) WHERE id={admin[0]}', (1,))
            else:
                sql_edit(f'UPDATE admins SET dob=dob+1 WHERE id={admin[0]}', ())
            
            if not intern[3]:
                sql_edit(f'UPDATE admins SET dob=(?) WHERE id={callback_query.from_user.id}', (1,))
            else:
                sql_edit(f'UPDATE admins SET dob=dob+1 WHERE id={callback_query.from_user.id}', ())
            
            admin_productivity = sql_select(f"SELECT * FROM daily_productivity WHERE id={admin[0]}")
            intern_productivity = sql_select(f"SELECT * FROM daily_productivity WHERE id={intern[0]}")
            
            if not intern_productivity:
                sql_edit(f'INSERT INTO daily_productivity VALUES(?, ?)',
                         (callback_query.from_user.id, 1))
            else:
                sql_edit(f'UPDATE daily_productivity SET productivity=productivity+1 '
                         f'WHERE id={callback_query.from_user.id}', ())
            
            if not admin_productivity:
                sql_edit(f'INSERT INTO daily_productivity VALUES(?, ?)',
                         (admin[0], 1))
            else:
                sql_edit(f'UPDATE daily_productivity SET productivity=productivity+1 '
                         f'WHERE id={admin[0]}', ())
            
            await callback_query.message.edit('✅')
        
        elif data.startswith('tutor'):
            msg = data.split(' ', 4)
            
            if callback_query.from_user.id != int(msg[3]):
                await callback_query.answer('☺️ Это не ваша кнопка!')
                return
            
            if msg[1] == '0':
                reputation = 'Плохая Репутация ⚠'
            elif msg[1] == '1':
                reputation = 'Возможно Скаммер ⚠'
            elif msg[1] == '2':
                reputation = 'СКАММЕР ⚠'
            elif msg[1] == '3':
                reputation = 'Петух 🐓'
            else:
                reputation = 'Неизвестно'
            
            sql_edit(f'UPDATE scammers SET reputation = (?) WHERE id = (?);',
                     (reputation, msg[2]))
            
            try:
                
                scammer = sql_select(f"SELECT * FROM scammers WHERE id={msg[2]}")[0]
                admin = sql_select(f'SELECT * FROM admins WHERE intern = {callback_query.from_user.id}')[0]
                
                await app.send_message(
                    chat_id=admin[0],
                    text=f'🆕 Заявка от {callback_query.from_user.mention}\n\n'
                         f'{scammer[0]}\n'
                         f'{scammer[2]}\n'
                         f'{scammer[3]}',
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(
                            '✅',
                            callback_data=f'approve {callback_query.from_user.id} {admin[0]}'),
                            InlineKeyboardButton(
                                '❌',
                                callback_data=f'del {msg[2]}')]]
                    )
                )
                await callback_query.message.edit(f"✅ <b>Информация была отправлена вашему куратору!</b>")
            
            except Exception as e:
                await callback_query.message.reply(f"⛔ <b>Что-то пошло не так!</b> @PapaBuyer {e}")
        
        elif data.startswith('change_reputation'):
            
            msg = data.split(' ', 3)
            
            if callback_query.from_user.id != int(msg[3]):
                await callback_query.answer('☺️ Это не ваша кнопка!')
                
            else:
                await callback_query.message.edit(
                    '🤔 Выберите репутацию',
                    reply_markup=InlineKeyboardMarkup([
                        
                        [InlineKeyboardButton('Плохая Репутация ⚠',
                                              callback_data=f'reputation 0 {msg[1]} {msg[2]}')],
                        
                        [InlineKeyboardButton('Возможно Скаммер ⚠',
                                              callback_data=f'reputation 1 {msg[1]} {msg[2]}')],
                        
                        [InlineKeyboardButton('СКАММЕР ⚠', callback_data=f'reputation 2 {msg[1]} {msg[2]}')],
                        
                        [InlineKeyboardButton('Петух 🐓', callback_data=f'reputation 3 {msg[1]} {msg[2]}')], ]))
            
        elif data.startswith('reputation'):
            
            msg = data.split(' ', 4)
            
            if callback_query.from_user.id != int(msg[3]):
                await callback_query.answer('☺️ Это не ваша кнопка!')
            else:
                try:
                    
                    if msg[1] == '0':
                        reputation = 'Плохая Репутация ⚠'
                    elif msg[1] == '1':
                        reputation = 'Возможно Скаммер ⚠'
                    elif msg[1] == '2':
                        reputation = 'СКАММЕР ⚠'
                    elif msg[1] == '3':
                        reputation = 'Петух 🐓'
                    else:
                        reputation = 'Неизвестно'
                    
                    sql_edit(f'UPDATE scammers SET reputation = (?) WHERE id = (?);',
                             (reputation, msg[2]))
                    
                    admin = sql_select(f"SELECT * FROM admins WHERE id={callback_query.from_user.id}")[0]
                    
                    if not admin[3]:
                        sql_edit(f'UPDATE admins SET dob=(?) WHERE id={callback_query.from_user.id}', (1,))
                    else:
                        sql_edit(f'UPDATE admins SET dob=dob+1 WHERE id={callback_query.from_user.id}', ())
                    
                    productivity = sql_select(f"SELECT * FROM daily_productivity "
                                              f"WHERE id={callback_query.from_user.id}")
                    
                    if not productivity:
                        sql_edit(f'INSERT INTO daily_productivity VALUES(?, ?)', (callback_query.from_user.id, 1))
                    else:
                        sql_edit(f'UPDATE daily_productivity SET productivity=productivity+1 '
                                 f'WHERE id={callback_query.from_user.id}', ())
                    
                    await callback_query.message.edit(
                        '<b>✅ | + 1 заявка</b>\n\n'
                        f'💪 Новое значение - {admin[3] + 1}\n\n'
                        f'ℹ️ #NotInLog.')
                
                
                except Exception as exc:
                    await app.send_message(DIMA, f'🦍 Ошибка в кнопке reputation: {exc}')
                    await callback_query.message.edit(exc)
                
                try:
                    await app.send_message(msg[1], '👀 Ваша репутация в базе была изменена',
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                               text='Чекнуть себя 🔎',
                                               callback_data=f'check {msg[1]}'
                                           )]]))
                    commands.changed += 1
                
                except Exception as e:
                    await app.send_message(DIMA, f'⛔ Не получилось отправить уведомление!\n\n<pre>{e}</pre>')
                
                scammer = sql_select(f"SELECT * FROM scammers WHERE id={msg[2]}")[0]
                
                try:
                    
                    keyboard = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(text='ℹ ПРОФИЛЬ ℹ️', user_id=msg[2])],
                        ]
                    
                    )
                    
                    posted_message = await app.send_message(-1001652069822, f'''
Админ {callback_query.from_user.mention} занёс нового человека в базу!
#id{callback_query.from_user.id} #занос_в_бд
=============
Данные о новом пользователе в БД:

<b>🆔 ID</b>: <code>{scammer[0]}</code>
<a href=/'tg://openmessage?user_id={scammer[0]}/'>Вечная Ссылка</a>
<b>⚖️ Репутация</b>: <code>{reputation}</code>
<b>📖 Описание</b>: <i>{scammer[3]}</i>
=============
Команда: <code>/scam {scammer[0]} scammer[3]</code>
                                            ''', reply_markup=keyboard)
                    await callback_query.message.edit(
                        '<b>✅ | + 1 заявка</b>\n\n'
                        f'💪 Новое значение - {admin[3] + 1}\n\n'
                        f'ℹ️ {posted_message.link}')
                
                except errors.ButtonUserPrivacyRestricted:
                    posted_message = await app.send_message(-1001652069822, f'''
Админ {callback_query.from_user.mention} занёс нового человека в базу!
#id{callback_query.from_user.id} #занос_в_бд
=============
Данные о новом пользователе в БД:

<b>🆔 ID</b>: <code>{scammer[0]}</code>
<a href=/'tg://openmessage?user_id={scammer[0]}/'>Вечная Ссылка</a>
<b>⚖️ Репутация</b>: <code>{reputation}</code>
<b>📖 Описание</b>: <i>{scammer[3]}</i>
=============
Команда: <code>/scam {scammer[0]} scammer[3]</code>''')
                    
                    await callback_query.message.edit(
                        '<b>✅ | + 1 заявка</b>\n\n'
                        f'💪 Новое значение - {admin[3] + 1}\n\n'
                        f'ℹ️ {posted_message.link}')
        
        
        elif data.startswith('privet'):
            await callback_query.answer('ладно')
        
        elif data.startswith('support'):
            
            await callback_query.message.edit(
                f'⚙ {callback_query.from_user.mention}, используйте кнопки ниже для навигации:',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('Слить скаммера 😡', callback_data='reportscammer')],
                    [InlineKeyboardButton('Сообщить о баге 🐞', callback_data='bugreport')],
                    [InlineKeyboardButton('Предложить идею 💡', callback_data='idea')],
                    [InlineKeyboardButton('Оставить отзыв 🦔💬', callback_data='vouch')],
                    [InlineKeyboardButton('Пожаловаться на проблему 😥', callback_data='gotatrouble')],
                ]))
        
        elif data.startswith('trade'):
            
            await add_to_net(callback_query.from_user.id)
            data = sql_select(f'SELECT free_deals FROM net WHERE id = {callback_query.from_user.id}')
            
            if data and data[0][0] > 0:
                try:
                    sql_edit(
                        f'UPDATE net SET free_deals = free_deals - 1 WHERE id = {callback_query.from_user.id}', ())
                    
                    await userbot.start()
                    
                    group = await userbot.create_group(title='Сделка через GASD 🌴', users='AntiScamDatabaseBot')
                    
                    link = (await userbot.create_chat_invite_link(group.id)).invite_link
                        
                    await userbot.stop()
                    
                    await app.send_message(
                        group.id,
                        '<a href=https://telegra.ph/file/952f65f85ddf10d64b4a5.png>\u200B</a>'
                        f'<b>{callback_query.from_user.mention}, вы успешно создали сделку!</b>\n\n'
                        'Скоро в группу зайдёт гарант. А пока что напишите, на что у вас сделка 👇')
                    
                    await app.send_message(
                        -1002101027116,
                        '<a href=https://telegra.ph/file/952f65f85ddf10d64b4a5.png>\u200B</a>'
                        f'<b>Новая сделка от {callback_query.from_user.mention}!</b>\n\n'
                        'Жмите кнопку ниже, чтобы зайти в группу',
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton('Перейти 💬', url=link)]]))
                    
                    
                    await callback_query.message.edit(
                        f'Зайдите в группу и напишите, на что у вас сделка - {link}\n\n'
                        f'Также пригласите в эту группу второго участника сделки ✨',
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton('Перейти 💬', url=link)],
                             [InlineKeyboardButton('Отправить ссылку', url=f't.me/share/url?url={link}')]]))
                except Exception as e:
                    await callback_query.message.reply(f'{e}')
            else:
                await callback_query.message.edit(
                    f'<b>⌛ Вы превысили лимит сделок в день,</b> попробуйте создать новую сделку завтра.\n\n'
                    f'(В день можно создавать только 2 сделки)',
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton('Скрыть', callback_data='hide')]]))

        
        elif data.startswith('delation'):
            
            peer = await app.resolve_peer(-1001949170455)
            
            data = await app.invoke(CreateForumTopic(channel=peer, title=f'🟢', random_id=app.rnd_id()))
            topic_id = data.updates[0].id
            
            await app.send_message(
                -1001949170455,
                '<a href=https://telegra.ph/file/5fdc0e48b596cd3fd7550.png>\u200B</a>'
                f'<b>{callback_query.from_user.mention}, добро пожаловать в чат с волонтёром!</b>\n\n'
                'Чтобы мы смогли помочь Вам, пожалуйста, в максимальных подробностях напишите, что случилось и '
                'как вас обманули. Если есть возможность прислать переписку или фото/ видео, которые помогут - '
                'это будет большим плюсом.',
                reply_to_message_id=topic_id)
            
            await app.send_message(
                -1002091856799,
                '<a href=https://telegra.ph/file/97faf8bb06675ffc3e764.png>\u200B</a>'
                f'<b>Новая жалоба от {callback_query.from_user.mention}!</b>\n\n'
                'Жмите кнопку ниже, чтобы её рассмотреть',
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton('Перейти 💬', url=f'https://t.me/ReportRoblox/{topic_id}')]]))
            
            await callback_query.message.edit(
                '<a href=https://telegra.ph/file/d9f3c88c3f0e36f89bb17.png>\u200B</a>'
                '<b>Перейдите в чат с волонтёром, используя кнопку ниже.</b>',
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton('Перейти 💬', url=f'https://t.me/ReportRoblox/{topic_id}')]]))
            
            sql_edit('INSERT INTO delations VALUES(?, ?)', (topic_id, callback_query.from_user.id))
        
        
        elif data.startswith('gotatrouble'):
            
            await callback_query.message.edit(
                '😥 Нам жаль, что вы столкнулись с проблемой в нашем проекте.\n\n'
                'Опишите суть проблемы одним сообщением, при необходимости прикрепите видео или фото',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton('Отмена ❌', callback_data='support')]]))
            
            async def wait(_, message):
                
                sent_message = await app.copy_message(
                    chat_id=-1001735865508,
                    from_chat_id=message.chat.id,
                    message_id=message.id)
                await sent_message.reply(
                    f'#ТРАБЛ от {message.from_user.mention}  <code>[{message.from_user.id}]</code>'
                )
                
                await callback_query.message.edit(
                    f'<b>✅ | Спасибо за ваш фидбек!\n\nЖалоба была успешно отправлена, ожидайте ответ админов',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton('Вернуться ↩️', callback_data='support')]]))
                await app.delete_messages(message.chat.id, message.id)
                
                # Остановить обработчик после получения первого сообщения
                app.remove_handler(wait_handler)
            
            # Создайте обработчик и присвойте его переменной
            wait_handler = MessageHandler(wait, filters.chat(
                callback_query.message.chat.id) & filters.user(callback_query.from_user.id))
            app.add_handler(wait_handler)
        
        
        elif data.startswith('vouch'):
            
            await callback_query.message.edit(
                '🦔💬 Спасибо, что решили оставить отзыв о нашем проекте.\n\n'
                'Мы принимаем как положительные, так и негативные отзывы, не бойтесь рассказать нам всё, что думаете'
                '\n\nНапишите отзыв одним сообщением, при необходимости прикрепите видео или фото ☺️',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton('Отмена ❌', callback_data='support')]]))
            
            async def wait(_, message):
                
                sent_message = await app.copy_message(
                    chat_id=-1001735865508,
                    from_chat_id=message.chat.id,
                    message_id=message.id)
                await sent_message.reply(
                    f'#ОТЗЫВ от {message.from_user.mention} <code>[{message.from_user.id}]</code>'
                )
                
                await callback_query.message.edit(
                    f'<b>✅ | Спасибо за ваш фидбек! Отзыв был успешно отправлен.',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton('Вернуться ↩️', callback_data='support')]]))
                await app.delete_messages(message.chat.id, message.id)
                
                # Остановить обработчик после получения первого сообщения
                app.remove_handler(wait_handler)
            
            # Создайте обработчик и присвойте его переменной
            wait_handler = MessageHandler(wait, filters.chat(
                callback_query.message.chat.id) & filters.user(callback_query.from_user.id))
            app.add_handler(wait_handler)
        
        elif data.startswith('appeal'):
            
            msg = data.split(' ', 2)
            
            if callback_query.from_user.id != int(msg[1]):
                await callback_query.answer('☺️ Это не ваша кнопка!')
                return
            
            await callback_query.answer('✅')
            
            sent = await app.send_message(
                callback_query.from_user.id,
                '<b>Хотите подать аппеляцию? 🤔</b>\n\n'
                'Если вы считаете, что вас добавили по ошибке, кратко опишите ситуацию и вашу проблему '
                'одним сообщением, при необходимости прикрепите видео или фото.\n\n'
                'Ваше сообщение будет отправлено админам на рассмотрение',
                reply_markup=HIDE_KB)
            
            async def wait(_, message):
                
                # Остановить обработчик после получения первого сообщения
                app.remove_handler(wait_handler)
                
                sent_message = await app.copy_message(
                    chat_id=-1001902750940,
                    from_chat_id=message.chat.id,
                    message_id=message.id)
                await sent_message.reply(f'#АППЕЛЯЦИЯ от {message.from_user.mention} '
                                         f'<pre>[{message.from_user.id}]</pre>')
                
                await sent.edit(
                    f'<b>✅ | Аппеляция была отправлена. Бот напишет вам, если вас удалят из базы.',
                    reply_markup=HIDE_KB)
                await app.delete_messages(message.chat.id, message.id)
            
            # Создайте обработчик и присвойте его переменной
            wait_handler = MessageHandler(wait, filters.chat(
                callback_query.message.chat.id) & filters.user(callback_query.from_user.id))
            app.add_handler(wait_handler)
        
        elif data.startswith('idea'):
            await callback_query.message.edit(
                '💡 Мы обожаем новые идеи и с радостью их реализуем!\n\n'
                'Напишите свою идею одним сообщением в лс боту, она будет отправлена напрямую владельцу',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton('Отмена ❌', callback_data='support')]]))
            
            async def wait(_, message):
                
                sent_message = await app.copy_message(
                    chat_id=-1001735865508,
                    from_chat_id=message.chat.id,
                    message_id=message.id)
                await sent_message.reply(
                    f'#ИДЕЯ от {message.from_user.mention} <code>[{message.from_user.id}]</code>'
                )
                
                await callback_query.message.edit(
                    f'<b>✅ | Спасибо за вашу идею! Она была успешно отправлена ✨',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton('Вернуться ↩️', callback_data='support')]]))
                await app.delete_messages(message.chat.id, message.id)
                
                # Остановить обработчик после получения первого сообщения
                app.remove_handler(wait_handler)
            
            # Создайте обработчик и присвойте его переменной
            wait_handler = MessageHandler(wait, filters.chat(
                callback_query.message.chat.id) & filters.user(callback_query.from_user.id))
            app.add_handler(wait_handler)
        
        
        elif data.startswith('bugreport'):
            await callback_query.message.edit(
                '🐞 Нам жаль, что вы столкнулись с багом в боте.'
                '\n\nОпишите суть бага одним сообщением, при необходимости прикрепите видео или фото',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton('Отмена ❌', callback_data='support')]]))
            
            async def wait(_, message):
                
                sent_message = await app.copy_message(
                    chat_id=-1001735865508,
                    from_chat_id=message.chat.id,
                    message_id=message.id)
                await sent_message.reply(
                    f'#БАГ от {message.from_user.mention} <code>[{message.from_user.id}]</code>'
                )
                
                await callback_query.message.edit(
                    f'<b>✅ | Спасибо за ваш фидбек! Жалоба была успешно отправлена.',
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton('Вернуться ↩️', callback_data='support')]]))
                await app.delete_messages(message.chat.id, message.id)
                
                # Остановить обработчик после получения первого сообщения
                app.remove_handler(wait_handler)
            
            # Создайте обработчик и присвойте его переменной
            wait_handler = MessageHandler(wait, filters.chat(
                callback_query.message.chat.id) & filters.user(callback_query.from_user.id))
            app.add_handler(wait_handler)
        
        
        elif data.startswith('channel'):
            
            if callback_query.message.chat.type == ChatType.PRIVATE:
                
                _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {callback_query.from_user.id}")
                _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {callback_query.from_user.id}")
                user_state = sql_select(f"SELECT * FROM net WHERE id = {callback_query.from_user.id}")
                
                if _fetchall_mms != [] or _fetchall_admins != [] or callback_query.from_user.id == 1032156461:
                    await callback_query.message.edit(f"📣 Введите ссылку на канал:",
                                                      reply_markup=InlineKeyboardMarkup([[
                                                          InlineKeyboardButton('Отмена ❌', callback_data='me')
                                                      ]]))
                    
                    async def wait(_, message):
                        
                        sql_edit(f'UPDATE net SET channel=(?) WHERE id={message.from_user.id}', (message.text,))
                        await app.send_message(
                            chat_id=-1001652069822,
                            text=f'{message.from_user.mention} поставил себе новый канал!'
                                 f'#id{message.from_user.id} #изменение_канала'
                                 f'<code>{user_state[0][4]}</code> ➡️ <code>{message.text}</code>')
                        
                        await callback_query.message.edit(
                            f'<b>✅ | Канал успешно обновлён</b>\n\nℹ️ {user_state[0][4]} ➡️ {message.text}',
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton('Мой профиль ↩️', callback_data='me')]]))
                        await app.delete_messages(message.chat.id, message.id)
                        
                        # Остановить обработчик после получения первого сообщения
                        app.remove_handler(wait_handler)
                    
                    # Создайте обработчик и присвойте его переменной
                    wait_handler = MessageHandler(wait, filters.chat(
                        callback_query.message.chat.id) & filters.user(callback_query.from_user.id))
                    app.add_handler(wait_handler)
                
                
                
                
                else:
                    await callback_query.answer(f"⛔ Доступно только гарантам и волонтёрам", show_alert=True)
            else:
                await callback_query.answer(f"⛔ Доступно только в лс с ботом", show_alert=True)
        
        elif data.startswith('me'):
            
            await callback_query.answer(f"🧿 Ваш профиль:")
            
            user_state = await add_to_net(callback_query.from_user.id)
            _fetchall_mms = sql_select(f"SELECT * FROM mms WHERE id = {callback_query.from_user.id}")
            _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {callback_query.from_user.id}")
            
            country = get_country_emojie(user_state[0][3])
            if not country:
                country = '🌏'
            
            if callback_query.message.chat.type == ChatType.PRIVATE:
                if not await check_sub(callback_query):
                    return
            
            keyboard = [
                [InlineKeyboardButton('🔎 Проверить себя', callback_data=f'check {callback_query.from_user.id}')],
                [InlineKeyboardButton('📣 Установить канал', callback_data='channel')],
                [InlineKeyboardButton(f'{country} Установить страну', callback_data='set country')],
                [InlineKeyboardButton('❓ Как пользоваться ботом', callback_data='howto')],
            ]
            
            if _fetchall_mms or _fetchall_admins:
                keyboard.append([InlineKeyboardButton("⭐ СКВАД ГАЗДА ⭐", callback_data='squad')])
            
            keyboard.append([InlineKeyboardButton("🌴 Наш Чат Общения", url='https://t.me/+goO620eaHQo0NjMy')])
            
            await callback_query.message.edit(
                f'ℹ️ {callback_query.from_user.mention}, используйте кнопки ниже для навигации\n\n'
                f'🔥 Скаммеров слито: {user_state[0][8]}\n'
                f'🔎 Вас искали {user_state[0][1]} раз',
                reply_markup=InlineKeyboardMarkup(keyboard))

            return
        
        elif data.startswith('got scammed'):
            our_group = await app.get_chat(report_group)
            await callback_query.message.edit(f'''
😭 <b>Вас скамнули?</b> Слейте скаммера в нашей группе @{our_group.username}

Как это сделать написано в этом посте - https://t.me/AntiScamRoblox/307
            ''', reply_markup=HIDE_KB)
        
        elif data.startswith('no proofs'):
            await callback_query.message.edit(
                '🥲 <b>Вас скамнули и нет пруфов?</b>\n\n'
                'Постарайтесь найти максимально много: скрины переписки, скрины трейдов, ники и переписки в игре '
                'и любую другую информацию, которая может помочь.\n\n'
                'Мы не добавляем людей без пруфов на скам, '
                'поэтому в будущем всегда скриньте переписку, чтобы у вас были пруфы!', reply_markup=HIDE_KB)
        
        elif data.startswith('check'):
                
            data = callback_query.data
            res = await check_person_by_id(await app.get_users(data.split()[1]))
                
            await app.edit_message_text(message_id=callback_query.message.id, chat_id=callback_query.message.chat.id,
                                        text=res, reply_markup=AS_REPORT_KB)
        
        elif data.startswith('alert+'):
            commands.shown += 1
            data = callback_query.data
            res = await check_person_by_id(await app.get_users(data.split()[1]))
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton('СПРЯТАТЬ 🐵', callback_data=f'alert- {data.split()[1]}')],
                [InlineKeyboardButton('ЗАБАНИТЬ ⛔', callback_data=f'ban {data.split()[1]}')]])
            
            await app.edit_message_text(message_id=callback_query.message.id,
                                        chat_id=callback_query.message.chat.id,
                                        text=res,
                                        reply_markup=keyboard)
        
        elif data.startswith('alert-'):
            commands.hidden += 1
            _fetchall_scammers = sql_select(f"SELECT * FROM scammers WHERE id = {data.split()[1]}")
            
            if not _fetchall_scammers:
                await callback_query.answer(
                    f"😳 Человека уже нет в базе",
                    show_alert=True)
                return
            
            person = await app.get_users(data.split()[1])
            
            text = f'''
<a href={random.choice(scam_pictures)}>\u200B</a>
⚠️ {person.mention} [<code>{data.split()[1]}</code>] находится в нашей базе. Будьте аккуратны при контактах с ним!

💙 <b>Репутация</b>: {_fetchall_scammers[0][2]}'''
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('РАЗВЕРНУТЬ 🙈',
                                                                   callback_data=f'alert+ {data.split()[1]}')],
                                             [InlineKeyboardButton('ЗАБАНИТЬ ⛔',
                                                                   callback_data=f'ban {data.split()[1]}')]])
            
            await app.edit_message_text(message_id=callback_query.message.id,
                                        chat_id=callback_query.message.chat.id,
                                        text=text,
                                        reply_markup=keyboard)
        
        elif data.startswith('become mm'):
            
            res = '''
<b>Как стать гарантом GASD?</b> 🌴

<i>Сейчас гарантом можно стать только по приглашению владельца базы. Следите за обновлениями на @StellarwayAgency</i>
            '''
            await app.edit_message_text(message_id=callback_query.message.id,
                                        chat_id=callback_query.message.chat.id,
                                        text=res,
                                        reply_markup=HIDE_KB)
        
        elif data.startswith('become admin'):
            res = '''
<b>Как стать волонтёром GASD?</b> 🌴

На данный момент единственный способ попасть к нам в команду - участвовать в наборах волонтёров

Информация о наборах волонтёров публикуется на @StellarwayAgency - подпишитесь)
                    '''
            await callback_query.message.reply(text=res, reply_markup=HIDE_KB)
        
        elif data.startswith('autoban'):
            
            status = await app.get_chat_member(chat_id=callback_query.message.chat.id,
                                               user_id=callback_query.from_user.id)
            
            if status.status == ChatMemberStatus.ADMINISTRATOR or status.status == ChatMemberStatus.OWNER:
                group = sql_select(f"SELECT * FROM groups WHERE id = {callback_query.message.chat.id}")[0]
                
                if not group[2]:
                    sql_edit(f'UPDATE groups SET ban=1 WHERE id={callback_query.message.chat.id}', ())
                else:
                    val = group[2]
                    if val < 2:
                        val += 1
                    else:
                        val = -1
                    
                    sql_edit(f'UPDATE groups SET ban=(?) WHERE id={callback_query.message.chat.id}', (val,))
                
                if group[3] == 1:
                    enabledalert = '✅'
                else:
                    enabledalert = '❌'
                
                if group[4] == 1:
                    enabledhelp = '✅'
                else:
                    enabledhelp = '❌'
                
                if group[2] == -1:
                    autoban = '❌ Автобан отключён'
                elif group[2] == 0:
                    autoban = '✅ Плохая репутация +'
                elif group[2] == 1:
                    autoban = '✅ Возможно Скаммер +'
                elif group[2] == 2:
                    autoban = '✅ Банить только Скаммеров'
                else:
                    autoban = '❓ Неизвестная ошибка'
                
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(f"АВТОБАН - ({autoban}) ✅",
                                           callback_data=f'autoban {callback_query.message.chat.id}')],
                     [InlineKeyboardButton(f"{enabledalert} ПРЕДУПРЕЖДЕНИЯ",
                                           callback_data=f'scamwarn {callback_query.message.chat.id}')],
                     [InlineKeyboardButton(f"{enabledhelp} СЛИТЬ СКАМЕРА",
                                           callback_data=f'slivscam {callback_query.message.chat.id}')]]
                )
                
                await app.edit_message_text(message_id=callback_query.message.id,
                                            chat_id=callback_query.message.chat.id,
                                            text='Первая кнопка отвечает за автобан. '
                                                 'Вы можете выбрать, начиная с какой '
                                                 'репутации пользователь будет забанен.\n\nВторая кнопка отвечает за '
                                                 'сообщения о том, что человек скам, если он пишет в чат.\n\nТретья '
                                                 'кнопка отвечает за предложение слить скаммера в нашем официальном '
                                                 'чате.\n\n\n<b>Настройки группы:</b>',
                                            reply_markup=keyboard)
            else:
                await callback_query.answer('❌ Доступно только владельцу и админам группы', show_alert=True)
        
        elif data.startswith('scamwarn'):
            
            status = await app.get_chat_member(chat_id=callback_query.message.chat.id,
                                               user_id=callback_query.from_user.id)
            
            if status.status == ChatMemberStatus.ADMINISTRATOR or status.status == ChatMemberStatus.OWNER:
                group = sql_select(f"SELECT * FROM groups WHERE id = {callback_query.message.chat.id}")[0]
                
                if group[3] == 0 or not group[3]:
                    sql_edit(f'UPDATE groups SET alert=1 WHERE id={callback_query.message.chat.id}', ())
                    enabledalert = '✅'
                else:
                    sql_edit(f'UPDATE groups SET alert=0 WHERE id={callback_query.message.chat.id}', ())
                    enabledalert = '❌'
                
                if group[4] == 1:
                    enabledhelp = '✅'
                else:
                    enabledhelp = '❌'
                
                if group[2] == -1:
                    autoban = '❌ Автобан отключён'
                elif group[2] == 0:
                    autoban = '✅ Плохая репутация +'
                elif group[2] == 1:
                    autoban = '✅ Возможно Скаммер +'
                elif group[2] == 2:
                    autoban = '✅ Банить только Скаммеров'
                else:
                    autoban = '❓ Неизвестная ошибка'
                
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(f"АВТОБАН - ({autoban}) ✅",
                                           callback_data=f'autoban {callback_query.message.chat.id}')],
                     [InlineKeyboardButton(f"{enabledalert} ПРЕДУПРЕЖДЕНИЯ",
                                           callback_data=f'scamwarn {callback_query.message.chat.id}')],
                     [InlineKeyboardButton(f"{enabledhelp} СЛИТЬ СКАМЕРА",
                                           callback_data=f'slivscam {callback_query.message.chat.id}')]]
                )
                
                await app.edit_message_text(message_id=callback_query.message.id,
                                            chat_id=callback_query.message.chat.id,
                                            text='Первая кнопка отвечает за автобан. Вы можете выбрать, '
                                                 'начиная с какой репутации пользователь будет забанен.'
                                                 '\n\nВторая кнопка отвечает за сообщения о том, что человек скам,'
                                                 ' если он пишет в чат.'
                                                 '\n\nТретья кнопка отвечает за предложение слить скаммера в нашем '
                                                 'официальном чате.\n\n\n<b>Настройки группы:</b>',
                                            reply_markup=keyboard)
            else:
                await callback_query.answer('❌ Доступно только владельцу и админам группы', show_alert=True)
         
        elif data.startswith('slivscam'):
            
            status = await app.get_chat_member(chat_id=callback_query.message.chat.id,
                                               user_id=callback_query.from_user.id)
            
            if status.status == ChatMemberStatus.ADMINISTRATOR or status.status == ChatMemberStatus.OWNER:
                
                group = sql_select(f"SELECT * FROM groups WHERE id = {callback_query.message.chat.id}")[0]
                
                if group[4] == 0 or not group[4]:
                    sql_edit(f'UPDATE groups SET help=1 WHERE id={callback_query.message.chat.id}', ())
                    enabledhelp = '✅'
                else:
                    sql_edit(f'UPDATE groups SET help=0 WHERE id={callback_query.message.chat.id}', ())
                    enabledhelp = '❌'
                
                if group[3] == 1:
                    enabledalert = '✅'
                else:
                    enabledalert = '❌'
                
                if group[2] == -1:
                    autoban = '❌ Автобан отключён'
                elif group[2] == 0:
                    autoban = '✅ Плохая репутация +'
                elif group[2] == 1:
                    autoban = '✅ Возможно Скаммер +'
                elif group[2] == 2:
                    autoban = '✅ Банить только Скаммеров'
                else:
                    autoban = '❓ Неизвестная ошибка'
                
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(f"АВТОБАН - ({autoban}) ✅",
                                           callback_data=f'autoban {callback_query.message.chat.id}')],
                     [InlineKeyboardButton(f"{enabledalert} ПРЕДУПРЕЖДЕНИЯ",
                                           callback_data=f'scamwarn {callback_query.message.chat.id}')],
                     [InlineKeyboardButton(f"{enabledhelp} СЛИТЬ СКАМЕРА",
                                           callback_data=f'slivscam {callback_query.message.chat.id}')]]
                )
                
                await app.edit_message_text(message_id=callback_query.message.id,
                                            chat_id=callback_query.message.chat.id,
                                            text='Первая кнопка отвечает за автобан. Вы можете выбрать, начиная с какой'
                                                 ' репутации пользователь будет забанен.\n\nВторая кнопка отвечает за '
                                                 'сообщения о том, что человек скам, если он пишет в чат.\n\nТретья '
                                                 'кнопка отвечает за предложение слить скаммера в нашем официальном '
                                                 'чате.\n\n\n<b>Настройки группы:</b>',
                                            reply_markup=keyboard)
            else:
                await callback_query.answer('❌ Доступно только владельцу и админам группы', show_alert=True)
        
        elif data.startswith('admins'):
            commands.admins += 1
            
            if callback_query.from_user.id in banned:
                await callback_query.answer(
                    f'ℹ️ Пожалуйста, дождитесь выполнения прошлого запроса',
                    show_alert=True)
                return
            
            banned.append(callback_query.from_user.id)
            
            admins = sql_select(f"SELECT * FROM admins")
            text = f'💪 <b>Админы ГАЗДа ({len(admins)} / 15):</b>\n'
            buttons = []
            
            msg = await app.edit_message_media(
                callback_query.message.chat.id,
                callback_query.message.id,
                InputMediaPhoto('https://telegra.ph/file/99f94a46ba5387df946c7.png'))
            
            await msg.edit(f'⏳ {callback_query.from_user.mention}, загружаем...\n\nℹ️ {random.choice(hints)}')
            
            for admin in admins:
                try:
                    
                    person = await app.get_users(admin[0])
                    
                    if admin[2] == 0:
                        role = '🍼👶'
                    elif admin[2] == 1:
                        role = '👋🤓'
                    elif admin[2] == 2:
                        role = '🔥🥸'
                    elif admin[2] == 3:
                        role = '🏆😎'
                    else:
                        role = '❓❓'
                    
                    buttons.append([InlineKeyboardButton(text=f'{role} {person.first_name}',
                                                         callback_data=f'check {admin[0]}')])
                
                except Exception as e:
                    await app.send_message(DIMA, f'Ошибка при составлении списка админов\n\n{e}')
                    pass
            
            buttons.append([InlineKeyboardButton("СТАТЬ АДМИНОМ 🔎", callback_data="become admin")])
            await msg.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons))
            
            banned.remove(callback_query.from_user.id)
        
        elif data.startswith('mms'):
            commands.mms += 1
            if callback_query.from_user.id in banned:
                await callback_query.answer(
                    f'ℹ️ Пожалуйста, дождитесь выполнения прошлого запроса',
                    show_alert=True
                )
                return
            
            banned.append(callback_query.from_user.id)
            
            mms = sql_select(f"SELECT * FROM mms")
            buttons = []
            
            msg = await app.edit_message_media(
                callback_query.message.chat.id,
                callback_query.message.id,
                InputMediaPhoto('https://telegra.ph/file/cbcdf145de97000c55dc1.png')
            )
            
            await msg.edit(f'⏳ {callback_query.from_user.mention}, загружаем...\n\nℹ️ {random.choice(hints)}')
            
            for mm in mms:
                user_state = await new_search(mm[0])
                
                try:
                    person = await app.get_users(mm[0])
                    buttons.append([InlineKeyboardButton(text=f' {person.first_name} | 🔎 {user_state[0][1]}',
                                                         callback_data=f'check {mm[0]}')])
                
                except Exception as e:
                    await app.send_message(DIMA, f'Ошибка при формировании списка гарантов\n\n{e}')
                    pass
            
            buttons.append([InlineKeyboardButton('КТО ТАКОЙ ГАРАНТ? 🤓', url='https://t.me/AntiScamRoblox/301')])
            buttons.append([InlineKeyboardButton("СТАТЬ ГАРАНТОМ 🦔", callback_data="become mm")])
            
            await msg.edit(text='', reply_markup=InlineKeyboardMarkup(buttons))
            banned.remove(callback_query.from_user.id)
        
        elif data.startswith('refresh donations'):
            
            the_latest_donation = sql_select('SELECT * FROM donations ORDER BY time DESC LIMIT 1')
            top_donation = sql_select('SELECT * FROM donations '
                                      f'WHERE {time.time()}<time+2592000 ORDER BY amount DESC LIMIT 1')
            
            try:
                await callback_query.message.edit(
                    '⚡ <b>ТОП ДОНАТ за последние 30 дней:\n\n'
                    f'{top_donation[0][1]} - {top_donation[0][3]}RUB</b>\n'
                    f'<i>{top_donation[0][2]}</i>'
                    '\n______\n\n'
                    '⏰ Последний донат:\n\n'
                    f'{the_latest_donation[0][1]} - {the_latest_donation[0][3]}RUB\n'
                    f'<i>{the_latest_donation[0][2]}</i>'
                    '\n______\n\n'
                    f'Актуально на {datetime.now()}'[:-10],
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton('Задонатить ⚡',
                                               url='https://www.donationalerts.com/c/samoironia')],
                         [InlineKeyboardButton('Обновить ↩', callback_data='refresh donations')]]
                    ))
            except Exception as e:
                await callback_query.answer(f'👀 Новых донатов ещё не было', show_alert=True)
                await app.send_message(DIMA, f'Ошибка при обновлении донатов\n\n<pre>{e}</pre>')
        
        elif data.startswith('in_dev'):
            await callback_query.answer('🛠️ Раздел в разработке', show_alert=True)
        
        elif data.startswith('good_morning'):
            await callback_query.answer(random.choice(good_morning_advices), show_alert=True)
        
        elif data.startswith('good_night'):
            await callback_query.answer(random.choice(good_night_advices), show_alert=True)
        
        elif data.startswith('faq'):
            a = int(data.split(' ', 2)[1])
            
            if a == 0:
                await callback_query.message.edit('💁‍♂️ Выберите вопрос из списка ниже:',
                                                  reply_markup=InlineKeyboardMarkup(
                                                      [[InlineKeyboardButton(
                                                          '🤔 Кто такой гарант?',
                                                          callback_data='faq 1')],
                                                          [InlineKeyboardButton(
                                                              '🔍 Как найти гаранта?',
                                                              callback_data='faq 2')],
                                                          [InlineKeyboardButton(
                                                              '🛡 Как стать админом?',
                                                              callback_data='faq 3')],
                                                          [InlineKeyboardButton(
                                                              '✅ Как стать гарантом?',
                                                              callback_data='faq 4')],
                                                          [InlineKeyboardButton(
                                                              '😡 Как слить скаммера?',
                                                              callback_data='faq 5')],
                                                          [InlineKeyboardButton(
                                                              '⌚ Когда набор на админов?',
                                                              callback_data='faq 6')],
                                                          [InlineKeyboardButton(
                                                              '💸 Можно ли купить роль в базе?',
                                                              callback_data='faq 7')],
                                                          [InlineKeyboardButton(
                                                              '💰 Можно ли купить снятие из базы?',
                                                              callback_data='faq 8')], ]
                                                  ))
            elif a == 1:
                await callback_query.message.edit('💁‍♂️ <b>Кто такой гарант?</b>\n\n'
                                                  '<a href=https://t.me/AntiScamRoblox/301>'
                                                  'У нас есть отдельный пост об этом (ТЫК)</a>',
                                                  reply_markup=InlineKeyboardMarkup([[
                                                      InlineKeyboardButton('Вернуться ↩️', callback_data='faq 0')]]))
            elif a == 2:
                await callback_query.message.edit('💁‍♂️ <b>Как найти гаранта?</b>\n\n'
                                                  'В лс с ботом жмём кнопку "Наша команда", и затем выбираем '
                                                  'раздел гарантов.\n\nБот отобразит вам проверенных людей, '
                                                  'которые не кинут вас при сделке 😉\n\n'
                                                  '<i>Если кнопок нет, пропишите /start</i>',
                                                  reply_markup=InlineKeyboardMarkup([[
                                                      InlineKeyboardButton('Вернуться ↩️', callback_data='faq 0')]]))
            elif a == 3:
                await callback_query.message.edit('💁‍♂️ <b>Как стать админом?</b>\n\n'
                                                  'Наборы проводятся в https://t.me/+O_oc8pG9bQljNTVi',
                                                  reply_markup=InlineKeyboardMarkup([[
                                                      InlineKeyboardButton('Вернуться ↩️', callback_data='faq 0')]]))
            elif a == 4:
                await callback_query.message.edit('💁‍♂️ <b>Как стать гарантом?</b>\n\n'
                                                  '🦔 <b>Условия становления гарантом в GASD</b>\n\n'
                                                  'Для становления гарантом нужно соответствовать ОДНОМУ '
                                                  'из пунктов ниже:\n\n'
                                                  '▫️ ЛИБО иметь топ доверку БОЛЕЕ 80К рублей\n'
                                                  '▫️ ЛИБО иметь более 400 пруфов '
                                                  '<i>(Не мусорных, пруфы по 50 руб не прокатят)</i>\n'
                                                  '▫️ ЛИБО иметь большое доверие от владельца @PapaBuyer\n\n'
                                                  'Текст выше про вас? '
                                                  'Пишите @Anya_its_here, что хотите стать гарантом ;)',
                                                  reply_markup=InlineKeyboardMarkup([[
                                                      InlineKeyboardButton('Вернуться ↩️', callback_data='faq 0')]]))
            elif a == 5:
                await callback_query.message.edit('💁‍♂️ <b>Как слить скаммера?</b>\n\n'
                                                  'Наша база предлагает 2 способа слива скаммеров:\n\n'
                                                  '1️⃣ Слить скаммера в нашей группе жалоб - @GasdReport\n'
                                                  '- <i>Заходите в группу и кидаете пруфы скама, админы их '
                                                  'рассматривают и принимают решение: заносить человека в базу '
                                                  'или нет.</i>\n\n'
                                                  '2️⃣ Слить скаммера через лс с ботом\n'
                                                  '- <i>В лс с ботом нажимаете кнопку "Слить скаммера" и '
                                                  'действуете согласно инструкции. Этот метод ещё в разработке'
                                                  'и может работать нестабильно\n\n'
                                                  'Если кнопок нет, пропишите /start</i>',
                                                  reply_markup=InlineKeyboardMarkup([[
                                                      InlineKeyboardButton('Вернуться ↩️', callback_data='faq 0')]]))
            elif a == 6:
                await callback_query.message.edit('💁‍♂️ <b>Когда набор на админов?</b>\n\n'
                                                  'В среднем наборы проходят 2 раза в месяц, вы можете '
                                                  'следить за ними на канале @AntiScamRoblox и в группе наборов '
                                                  '(https://t.me/+O_oc8pG9bQljNTVi)',
                                                  reply_markup=InlineKeyboardMarkup([[
                                                      InlineKeyboardButton('Вернуться ↩️', callback_data='faq 0')]]))
            elif a == 7:
                await callback_query.message.edit('💁‍♂️ <b>Можно ли купить роль в базе?</b>\n\n'
                                                  'НЕТ. Мы НЕ продаём админки/ роли гарантов в нашей базе. '
                                                  'Если вы хотите поддержать нашу базу, жмите кноку "Донаты 💸"',
                                                  reply_markup=InlineKeyboardMarkup([[
                                                      InlineKeyboardButton('Вернуться ↩️', callback_data='faq 0')]]))
            elif a == 8:
                await callback_query.message.edit('💁‍♂️ <b>Можно ли купить снятие из базы?</b>\n\n'
                                                  'НЕТ. Мы НЕ удаляем пользователей. Наша цель - быть надёжным '
                                                  'и честным источником информации, который сможет помочь людям.',
                                                  reply_markup=InlineKeyboardMarkup([[
                                                      InlineKeyboardButton('Вернуться ↩️', callback_data='faq 0')]]))
    
        elif data.startswith('top_reporters'):
            
            await callback_query.message.edit('😎')
            await app.send_chat_action(callback_query.message.chat.id, ChatAction.TYPING)
            
            leaders = sql_select(f'SELECT id, contribution FROM net ORDER BY contribution DESC LIMIT 8')
            
            user_is_leader = False
            
            text = ('🏆 <b>Топ по количеству слитых скаммеров:</b>\n'
                    '<a href=https://telegra.ph/file/cff90a1e4873fe560010e.png>\u200B</a>\n')
            
            i = 0
            for leader in leaders:
                
                i += 1
                try:
                    if leader[0] == callback_query.from_user.id:
                        
                        user_is_leader = True
                        text += f'<b>{numberEmojies[i]} 🥷{leader[1]} {callback_query.from_user.mention[:]}</b>\n'
                    
                    else:
                        
                        user = await app.get_users(leader[0])
                        text += f'{numberEmojies[i]} <code>🥷</code>{leader[1]} {user.mention[:]}\n'
                
                except Exception:
                    pass
            
            if not user_is_leader:
                all_sorted = sql_select(f'SELECT id FROM net ORDER BY contribution DESC')
                rating = 0
                for user in all_sorted:
                    rating += 1
                    if user[0] == callback_query.from_user.id:
                        text += f'\nℹ️ <b>Ваша позиция в рейтинге - {rating}</b>'
                        break
            
            text += f'\n<a href=https://t.me/+rOaEL4igLQVhMjVi>{random.choice(lol)} Чат для слива скаммеров</a>'
            
            await callback_query.message.edit(text, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Статистика ✨', callback_data='stats')],
                [InlineKeyboardButton('Топ админов 😎', callback_data='top_admins'),
                 InlineKeyboardButton('Топ популярных 🐱', callback_data='top_mms')]]))
            
            await app.send_chat_action(callback_query.message.chat.id, ChatAction.CANCEL)
            return
        
        elif data.startswith('top_admins'):
            
            await callback_query.message.edit('😎')
            await app.send_chat_action(callback_query.message.chat.id, ChatAction.TYPING)
            
            leaders = sql_select(f'SELECT id, dob FROM admins ORDER BY dob DESC LIMIT 8')
            
            user_is_leader = False
            
            text = ('🏆 <b>Топ самых продуктивных админов:</b>\n'
                    '<a href=https://telegra.ph/file/cff90a1e4873fe560010e.png>\u200B</a>\n')
            
            i = 0
            for leader in leaders:
                
                i += 1
                try:
                    if leader[0] == callback_query.from_user.id:
                        
                        user_is_leader = True
                        text += f'<b>{numberEmojies[i]} 🤠{leader[1]} {callback_query.from_user.mention[:]}</b>\n'
                    
                    else:
                        
                        user = await app.get_users(leader[0])
                        text += f'{numberEmojies[i]} <code>🤠</code>{leader[1]} {user.mention[:]}\n'
                
                except Exception:
                    pass
            
            _fetchall_admins = sql_select(f"SELECT * FROM admins WHERE id = {callback_query.from_user.id}")
            
            if not user_is_leader and _fetchall_admins:
                all_sorted = sql_select(f'SELECT id FROM admins ORDER BY dob DESC')
                rating = 0
                for user in all_sorted:
                    rating += 1
                    if user[0] == callback_query.from_user.id:
                        text += f'\nℹ️ <b>Ваша позиция в рейтинге - {rating}</b>'
                        break
            
            text += f'\n<a href=https://t.me/+rOaEL4igLQVhMjVi>{random.choice(lol)} Чат для слива скаммеров</a>'
            
            await callback_query.message.edit(text, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Статистика ✨', callback_data='stats')],
                [InlineKeyboardButton('Топ по сливам 🌴', callback_data='top_admins'),
                 InlineKeyboardButton('Топ популярных 🐱', callback_data='top_mms')]]))
            
            await app.send_chat_action(callback_query.message.chat.id, ChatAction.CANCEL)
            return
        
        elif data.startswith('top_mms'):
            
            await callback_query.message.edit('😎')
            await app.send_chat_action(callback_query.message.chat.id, ChatAction.TYPING)
            
            leaders = sql_select(f'SELECT id, searches FROM net ORDER BY searches DESC LIMIT 8')
            
            user_is_leader = False
            
            text = ('🏆 <b>Топ самых популярных пользователей:</b>\n'
                    '<a href=https://telegra.ph/file/cff90a1e4873fe560010e.png>\u200B</a>\n')
            
            i = 0
            for leader in leaders:
                
                i += 1
                try:
                    if leader[0] == callback_query.from_user.id:
                        
                        user_is_leader = True
                        text += f'<b>{numberEmojies[i]} 🌴{leader[1]} {callback_query.from_user.mention[:]}</b>\n'
                    
                    else:
                        
                        user = await app.get_users(leader[0])
                        text += f'{numberEmojies[i]} <code>🌴</code>{leader[1]} {user.mention[:]}\n'
                
                except Exception:
                    pass
            
            if not user_is_leader:
                all_sorted = sql_select(f'SELECT id FROM net ORDER BY searches DESC')
                rating = 0
                for user in all_sorted:
                    rating += 1
                    if user[0] == callback_query.from_user.id:
                        text += f'\nℹ️ <b>Ваша позиция в рейтинге - {rating}</b>'
                        break
            
            text += f'\n<a href=https://t.me/+rOaEL4igLQVhMjVi>{random.choice(lol)} Чат для слива скаммеров</a>'
            
            await callback_query.message.edit(text, reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton('Статистика ✨', callback_data='stats')],
                [InlineKeyboardButton('Топ админов 😎', callback_data='top_admins'),
                 InlineKeyboardButton('Топ по сливам 🌴', callback_data='top_mms')]]))
            
            await app.send_chat_action(callback_query.message.chat.id, ChatAction.CANCEL)
            return
        
        elif data.startswith('stats'):
            global the_most_recent_search
            
            await callback_query.message.edit(f'''
{callback_query.from_user.mention}, ниже находится статистика нашего бота:
<a href=https://telegra.ph/file/cff90a1e4873fe560010e.png>\u200B</a>
🚫 Скаммеров в базе: {sql_select("SELECT COUNT(id) from scammers;")[0][0]}
👁️ Пользователей бота: {sql_select("SELECT COUNT(id) from users WHERE active=1;")[0][0]}

⚖️ Админов: {sql_select("SELECT COUNT(id) from admins;")[0][0]}
💸 Гарантов: {sql_select("SELECT COUNT(id) from mms;")[0][0]}
🏆️ Проверенных: {sql_select("SELECT COUNT(id) from net WHERE is_trusted > 0;")[0][0]}

🎉 Бот уже в {sql_select("SELECT COUNT(id) from groups;")[0][0]} группах

🔎 Поисков по базе за всё время: {sql_select("SELECT SUM(searches) from net WHERE searches > 0")[0][0]}
🌴 В последний раз искали: {the_most_recent_search}
                    ''', reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Топ по сливам 🌴', callback_data='top_reporters')],
                [InlineKeyboardButton('Топ админов 😎', callback_data='top_admins'),
                 InlineKeyboardButton('Топ популярных 🐱', callback_data='top_mms')]]))
        
        
async def setup_good_mood(app):
    await app.start()
    await app.send_message(DIMA, '👋')
    if (await app.get_me()).id == 6066255260:
        await app.send_message(DIMA, 'Я запустился с хорошим настроением 🙂')
        while True:
            await asyncio.sleep(1)
            hour = int(datetime.now().hour)
            minute = int(datetime.now().minute)
            second = int(datetime.now().second)
            if hour == 6 and minute == 0 and second == 0:
                try:
                    await app.send_photo(-1002091856799, random.choice(good_morning_pictures),
                                         'Доброе утро ☀️',
                                         reply_markup=InlineKeyboardMarkup([[
                                             InlineKeyboardButton('☺️', callback_data='good_morning')]]))
                    await app.send_photo(-1002101027116, random.choice(good_morning_pictures),
                                         'Доброе утро ☀️',
                                         reply_markup=InlineKeyboardMarkup([[
                                             InlineKeyboardButton('☺️', callback_data='good_morning')]]))
                    await app.send_document(1032156461, 'database.db')
                except Exception as e:
                    await app.send_message(1032156461, f'{e}')
            
            elif hour == 22 and minute == 30 and second == 0:
                
                sql_edit('UPDATE net SET free_checks = 10', ())
                sql_edit('UPDATE net SET free_deals = 2', ())
                
                try:
                    await app.send_message(
                        -1002091856799,
                        '<b>Подводим итоги дня 🌴</b>\n\n'
                        f'Новых заявок за день: '
                        f'{sql_select("SELECT SUM(productivity) FROM daily_productivity")[0][0]}'
                        f'\n#day_results')
                    
                    productivity = sql_select('SELECT * FROM daily_productivity ORDER BY productivity DESC')
                    popularity = sql_select('SELECT * FROM daily_searches ORDER BY searches DESC')
                    sql_edit('DELETE FROM daily_productivity', ())
                    sql_edit('DELETE FROM daily_searches', ())
                    
                    productivity_text = '❤️ <b>Сегодняшний топ админов:</b>\n\n'
                    iter1 = 0
                    
                    for admin in productivity:
                        iter1 += 1
                        person = await app.get_users(admin[0])
                        productivity_text += f'<b>{iter1} | {person.mention}</b>\n{admin[1]} ✅ Заявок\n\n'
                    
                    productivity_text += '🚀 <b>Дальше - больше</b>'
                    
                    popularity_text = '❤️ <b>Сегодняшний топ гарантов:</b>\n\n'
                    iter2 = 0
                    
                    for mm in popularity:
                        iter2 += 1
                        person = await app.get_users(mm[0])
                        popularity_text += f'<b>{iter2} | {person.mention}</b>\nИскали 🔍 {mm[1]} раз\n\n'
                    
                    popularity_text += '🚀 <b>Дальше - больше</b>'
                    
                    await app.send_message(-1002091856799, productivity_text)
                    if len(popularity) < 50:
                        await app.send_message(-1002101027116, popularity_text)
                    
                    await app.send_photo(-1002091856799, random.choice(good_night_pictures),
                                         'Спокойной ночи 🌙',
                                         reply_markup=InlineKeyboardMarkup([[
                                             InlineKeyboardButton('😴', callback_data='good_night')]]))
                    await app.send_photo(-1002101027116, random.choice(good_night_pictures),
                                         'Спокойной ночи 🌙',
                                         reply_markup=InlineKeyboardMarkup([[
                                             InlineKeyboardButton('😴', callback_data='good_night')]]))
                    
                    await app.send_document(1032156461, 'database.db')
                
                except Exception as e:
                    await app.send_message(1032156461, f'{e}')

for app in apps:
    app.run(setup_good_mood(app))
    idle()
    
for app in apps:
    app.send_document(1032156461, 'database.db')
    app.stop()
