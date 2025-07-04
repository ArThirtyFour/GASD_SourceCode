from datetime import datetime
from config import months


async def get_date():
    return str(datetime.now().day) + ' ' + months[datetime.now().month] + ' ' + str(datetime.now().year)


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    

def get_country(country_code):
    if country_code == 'ru':
        country = "Россия 🇷🇺"
    elif country_code == 'ua':
        country = "Украина 🇺🇦"
    elif country_code == 'kz':
        country = "Казахстан 🇰🇿"
    elif country_code == 'uz':
        country = "Узбекистан 🇺🇿"
    elif country_code == 'eu':
        country = "Европа 🇪🇺"
    elif country_code == 'us':
        country = "США 🇺🇸"
    elif country_code == 'by':
        country = "Беларусь 🇧🇾"
    elif country_code == 'tj':
        country = "Таджикистан 🇹🇯"
    elif country_code == 'az':
        country = "Азейбарджан 🇦🇿"
    elif country_code == 'tm':
        country = "Туркменистан 🇹🇲"
    elif country_code == 'lt':
        country = "Литва 🇱🇹"
    elif country_code == 'lv':
        country = "Латвия 🇱🇻"
    elif country_code == 'kg':
        country = "Кыргызстан 🇰🇬"
    elif country_code == 'ge':
        country = "Грузия 🇬🇪"
    elif country_code == 'am':
        country = "Армения 🇦🇲"
    elif country_code == 'sk':
        country = "Словакия 🇸🇰"
    elif country_code == 'md':
        country = "Молдавия 🇲🇩"
    elif country_code == 'pl':
        country = "Польша 🇵🇱"
    elif country_code == 'ee':
        country = "Эстония 🇪🇪"
    elif country_code == 'cz':
        country = "Чехия 🇨🇿"
    elif country_code == 'tr':
        country = "Турция 🇹🇷"
    elif country_code == 'th':
        country = "Таиланд 🇹🇭"
    elif country_code == 'de':
        country = "Германия 🇩🇪"
    elif country_code == 'fr':
        country = "Франция 🇫🇷"
    elif country_code == 'gb':
        country = "Великобритания 🇬🇧"
    elif country_code == 'es':
        country = "Испания 🇪🇸"
    elif country_code == 'it':
        country = "Италия 🇮🇹"
    elif country_code == 'nl':
        country = "Нидерланды 🇳🇱"
    elif country_code == 'se':
        country = "Швеция 🇸🇪"
    elif country_code == 'dk':
        country = "Дания 🇩🇰"
    elif country_code == 'fi':
        country = "Финляндия 🇫🇮"
    elif country_code == 'ch':
        country = "Швейцария 🇨🇭"
    elif country_code == 'at':
        country = "Австрия 🇦🇹"
    elif country_code == 'gr':
        country = "Греция 🇬🇷"
    elif country_code == 'is':
        country = "Исландия 🇮🇸"
    elif country_code == 'ph':
        country = "Филиппины 🇵🇭"
    elif country_code == 'ke':
        country = "Кения 🇰🇪"
    elif country_code == 'jp':
        country = "Япония 🇯🇵"
    elif country_code == 'vn':
        country = "Вьетнам 🇻🇳"
    elif country_code == 'hk':
        country = "Гонконг 🇭🇰"
    elif country_code == 'cn':
        country = "Китай 🇨🇳"
    elif country_code == 'kr':
        country = "Корея 🇰🇷"
    elif country_code == 'in':
        country = "Индия 🇮🇳"
    elif country_code == 'id':
        country = "Индонезия 🇮🇩"
    elif country_code == 'kp':
        country = "КНДР 🇰🇵"
    elif country_code == 'ae':
        country = "ОАЭ 🇦🇪"
    elif country_code == 'co':
        country = "Колумбия 🇨🇴"
    elif country_code == 'ca':
        country = "Канада 🇨🇦"
    elif country_code == 'us':
        country = "США 🇺🇸"
    elif country_code == 'au':
        country = "Австралия 🇦🇺"
    elif country_code == 'mx':
        country = "Мексика 🇲🇽"
    elif country_code == 'br':
        country = "Бразилия 🇧🇷"
    elif country_code == 'qa':
        country = "Катар 🇶🇦"
    elif country_code == 'sa':
        country = "Саудовская Аравия 🇸🇦"
    elif country_code == 'il':
        country = "Израиль 🇮🇱"
    elif country_code == 'pk':
        country = "Пакистан 🇵🇰"
    elif country_code == 'rs':
        country = "Сербия 🇷🇸"
    elif country_code == 'me':
        country = "Черногория 🇲🇪"
    else:
        country = None
    
    return country


def get_country_emojie(country_code):
    if country_code == 'ru':
        country = "🇷🇺"
    elif country_code == 'ua':
        country = "🇺🇦"
    elif country_code == 'kz':
        country = "🇰🇿"
    elif country_code == 'uz':
        country = "🇺🇿"
    elif country_code == 'eu':
        country = "🇪🇺"
    elif country_code == 'us':
        country = "🇺🇸"
    elif country_code == 'by':
        country = "🇧🇾"
    elif country_code == 'tj':
        country = "🇹🇯"
    elif country_code == 'az':
        country = "🇦🇿"
    elif country_code == 'tm':
        country = "🇹🇲"
    elif country_code == 'lt':
        country = "🇱🇹"
    elif country_code == 'lv':
        country = "🇱🇻"
    elif country_code == 'kg':
        country = "🇰🇬"
    elif country_code == 'ge':
        country = "🇬🇪"
    elif country_code == 'am':
        country = "🇦🇲"
    elif country_code == 'sk':
        country = "🇸🇰"
    elif country_code == 'md':
        country = "🇲🇩"
    elif country_code == 'pl':
        country = "🇵🇱"
    elif country_code == 'ee':
        country = "🇪🇪"
    elif country_code == 'cz':
        country = "🇨🇿"
    elif country_code == 'tr':
        country = "🇹🇷"
    elif country_code == 'th':
        country = "🇹🇭"
    elif country_code == 'de':
        country = "🇩🇪"
    elif country_code == 'fr':
        country = "🇫🇷"
    elif country_code == 'gb':
        country = "🇬🇧"
    elif country_code == 'es':
        country = "🇪🇸"
    elif country_code == 'it':
        country = "🇮🇹"
    elif country_code == 'nl':
        country = "🇳🇱"
    elif country_code == 'se':
        country = "🇸🇪"
    elif country_code == 'dk':
        country = "🇩🇰"
    elif country_code == 'fi':
        country = "🇫🇮"
    elif country_code == 'ch':
        country = "🇨🇭"
    elif country_code == 'at':
        country = "🇦🇹"
    elif country_code == 'gr':
        country = "🇬🇷"
    elif country_code == 'is':
        country = "🇮🇸"
    elif country_code == 'ph':
        country = "🇵🇭"
    elif country_code == 'ke':
        country = "🇰🇪"
    elif country_code == 'jp':
        country = "🇯🇵"
    elif country_code == 'vn':
        country = "🇻🇳"
    elif country_code == 'hk':
        country = "🇭🇰"
    elif country_code == 'cn':
        country = "🇨🇳"
    elif country_code == 'kr':
        country = "🇰🇷"
    elif country_code == 'in':
        country = "🇮🇳"
    elif country_code == 'id':
        country = "🇮🇩"
    elif country_code == 'kp':
        country = "🇰🇵"
    elif country_code == 'ae':
        country = "🇦🇪"
    elif country_code == 'co':
        country = "🇨🇴"
    elif country_code == 'ca':
        country = "🇨🇦"
    elif country_code == 'us':
        country = "🇺🇸"
    elif country_code == 'au':
        country = "🇦🇺"
    elif country_code == 'mx':
        country = "🇲🇽"
    elif country_code == 'br':
        country = "🇧🇷"
    elif country_code == 'qa':
        country = "🇶🇦"
    elif country_code == 'sa':
        country = "🇸🇦"
    elif country_code == 'il':
        country = "🇮🇱"
    elif country_code == 'pk':
        country = "🇵🇰"
    elif country_code == 'rs':
        country = "🇷🇸"
    elif country_code == 'me':
        country = "🇲🇪"
    else:
        country = None
    
    return country
