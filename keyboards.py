from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)

MAIN_KB = ReplyKeyboardMarkup(
    keyboard=[
        ["Мой профиль ℹ️"],
        ["Провести сделку 💰", "Слить скаммера 😡"],
        ["Гаранты ❤️‍🔥", "Волонтёры 🌴"],
        ["Статистика 📊", "FAQ ❓"],
    ],
    resize_keyboard=True
)

AS_REPORT_KB = InlineKeyboardMarkup(
    [[InlineKeyboardButton('КТО ТАКОЙ ГАРАНТ? 🤓', url='https://t.me/AntiScamRoblox/301')],
     [InlineKeyboardButton("⛔️️ СЛИТЬ СКАММЕРА ⛔️", url="https://t.me/+Gwu0EEzJTYQ4YTE6")]]
)

CHANNEL_KB = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🦔 ГРУППА ЖАЛОБ 🦔", url="https://t.me/+3O_1kOfRYNZmYTUy")]]
)

HIDE_KB = InlineKeyboardMarkup([[InlineKeyboardButton("Скрыть", callback_data="hide")]])

DEFAULT_KB = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "👍 ДОБАВИТЬ В ЧАТ 👍",
                url="https://t.me/AntiscamDatabaseBot?startgroup=new"
            )
        ]
    ]
)
WHAT_TO_DO_KB = InlineKeyboardMarkup(
    [[InlineKeyboardButton('... Если скамнули? 🤬', callback_data="got scammed")],
     [InlineKeyboardButton("... Если нет пруфов? 😭", callback_data="no proofs")]]
)

COUNTRIES_1 = InlineKeyboardMarkup([
    [InlineKeyboardButton('🇷🇺', callback_data='country ru'),
     InlineKeyboardButton('🇺🇦', callback_data='country ua'),
     InlineKeyboardButton('🇰🇿', callback_data='country kz'),
     InlineKeyboardButton('🇧🇾', callback_data='country by')],
    
    [InlineKeyboardButton('🇺🇿', callback_data='country uz'),
     InlineKeyboardButton('🇹🇯', callback_data='country tj'),
     InlineKeyboardButton('🇦🇿', callback_data='country az'),
     InlineKeyboardButton('🇹🇲', callback_data='country tm')],
    
    [InlineKeyboardButton('🇱🇹', callback_data='country lt'),
     InlineKeyboardButton('🇱🇻', callback_data='country lv'),
     InlineKeyboardButton('🇰🇬', callback_data='country kg'),
     InlineKeyboardButton('🇬🇪', callback_data='country ge')],
    
    [InlineKeyboardButton('🇦🇲', callback_data='country am'),
     InlineKeyboardButton('🇸🇰', callback_data='country sk'),
     InlineKeyboardButton('🇲🇩', callback_data='country md'),
     InlineKeyboardButton('🇵🇱', callback_data='country pl')],
    
    [InlineKeyboardButton('🇪🇪', callback_data='country ee'),
     InlineKeyboardButton('🇨🇿', callback_data='country cz'),
     InlineKeyboardButton('🇹🇷', callback_data='country tr'),
     InlineKeyboardButton('🇹🇭', callback_data='country th')],
    
    [InlineKeyboardButton('🇩🇪', callback_data='country de'),
     InlineKeyboardButton('🇫🇷', callback_data='country fr'),
     InlineKeyboardButton('🇬🇧', callback_data='country gb'),
     InlineKeyboardButton('🇪🇸', callback_data='country es')],
    
    [InlineKeyboardButton('🇮🇹', callback_data='country it'),
     InlineKeyboardButton('🇳🇱', callback_data='country nl'),
     InlineKeyboardButton('🇸🇪', callback_data='country se'),
     InlineKeyboardButton('🇩🇰', callback_data='country dk')],
    
    [InlineKeyboardButton('🇫🇮', callback_data='country fi'),
     InlineKeyboardButton('🇨🇭', callback_data='country ch'),
     InlineKeyboardButton('🇦🇹', callback_data='country at'),
     InlineKeyboardButton('🇬🇷', callback_data='country gr')],
    
    [InlineKeyboardButton('🇮🇸', callback_data='country is'),
     InlineKeyboardButton('🇵🇭', callback_data='country ph'),
     InlineKeyboardButton('🇰🇪', callback_data='country ke'),
     InlineKeyboardButton('🇯🇵', callback_data='country jp')],
    
    [InlineKeyboardButton('🇻🇳', callback_data='country vn'),
     InlineKeyboardButton('🇭🇰', callback_data='country hk'),
     InlineKeyboardButton('🇨🇳', callback_data='country cn'),
     InlineKeyboardButton('🇰🇷', callback_data='country kr')],
    
    [InlineKeyboardButton('🇮🇳', callback_data='country in'),
     InlineKeyboardButton('🇮🇩', callback_data='country id'),
     InlineKeyboardButton('🇰🇵', callback_data='country kp'),
     InlineKeyboardButton('🇦🇪', callback_data='country ae')],
    
    [InlineKeyboardButton('🇨🇴', callback_data='country co'),
     InlineKeyboardButton('🇨🇦', callback_data='country ca'),
     InlineKeyboardButton('🇺🇸', callback_data='country us'),
     InlineKeyboardButton('🇦🇺', callback_data='country au')],
    
    [InlineKeyboardButton('🇲🇽', callback_data='country mx'),
     InlineKeyboardButton('🇧🇷', callback_data='country br'),
     InlineKeyboardButton('🇶🇦', callback_data='country qa'),
     InlineKeyboardButton('🇸🇦', callback_data='country sa')],
    
    [InlineKeyboardButton('🇮🇱', callback_data='country il'),
     InlineKeyboardButton('🇵🇰', callback_data='country pk'),
     InlineKeyboardButton('🇷🇸', callback_data='country rs'),
     InlineKeyboardButton('🇲🇪', callback_data='country me')],
    
    [InlineKeyboardButton('Секрет 🌐', callback_data='country secret')],
    [InlineKeyboardButton('Отмена ❌', callback_data='me')],
])
