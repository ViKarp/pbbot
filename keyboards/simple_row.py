from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    if len(items) < 3:
        row = [KeyboardButton(text=item) for item in items]
        return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)
    if len(items) < 5:
        row1 = [KeyboardButton(text=item) for item in items[:3]]
        row2 = [KeyboardButton(text=item) for item in items[3:]]
        return ReplyKeyboardMarkup(keyboard=[row1, row2], resize_keyboard=True)
    if len(items) < 7:
        row1 = [KeyboardButton(text=item) for item in items[:3]]
        row2 = [KeyboardButton(text=item) for item in items[3:5]]
        row3 = [KeyboardButton(text=item) for item in items[5:]]
        return ReplyKeyboardMarkup(keyboard=[row1, row2, row3], resize_keyboard=False)
    if len(items) < 9:
        row1 = [KeyboardButton(text=item) for item in items[:3]]
        row2 = [KeyboardButton(text=item) for item in items[3:5]]
        row3 = [KeyboardButton(text=item) for item in items[5:7]]
        row4 = [KeyboardButton(text=item) for item in items[7:]]
        return ReplyKeyboardMarkup(keyboard=[row1, row2, row3, row4], resize_keyboard=False)


def make_catalog_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру с кнопками
    :return: объект инлайн-клавиатуры
    """
    buttons = [
        [
            InlineKeyboardButton(text="Значки", callback_data="badges"),
            InlineKeyboardButton(text="Пины", callback_data="pins")
        ],
        [
            InlineKeyboardButton(text="Стикеры", callback_data="stickers"),
            InlineKeyboardButton(text="Обложки", callback_data="covers")
        ],
        [
            InlineKeyboardButton(text="Ручки", callback_data="pens"),
            InlineKeyboardButton(text="Браслеты", callback_data="bracelets")
        ],
        [
            InlineKeyboardButton(text="Блокноты", callback_data="notebooks"),
            InlineKeyboardButton(text="Кружки", callback_data="cups")
        ],
        [
            InlineKeyboardButton(text="Бутылки", callback_data="bottles"),
            InlineKeyboardButton(text="Термокружки", callback_data="thermal_mugs")
        ],
        [
            InlineKeyboardButton(text="Футболки", callback_data="t-shirts"),
            InlineKeyboardButton(text="Свитшоты", callback_data="sweatshirts")
        ],
        [
            InlineKeyboardButton(text="Кофты", callback_data="sweaters"),
            InlineKeyboardButton(text="Худи", callback_data="hoodie")
        ],
        [InlineKeyboardButton(text="Магнитные планеры", callback_data="gliders")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard