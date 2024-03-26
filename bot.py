#!venv/bin/python
# -*- encoding: utf-8 -*-
import asyncio
import logging

import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import BaseFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import classes
import handlers.shop
from keyboards.simple_row import make_row_keyboard, make_catalog_keyboard


class EmailFilter(BaseFilter):
    def __init__(self, chat_type: str):
        self.chat_type = chat_type

    async def __call__(self, message: types.Message) -> bool:  # [3]
        return isinstance(self.chat_type, str) and "email" in self.chat_type


class User:
    name = ""
    key = ""
    confirm = False
    account = classes.Account()
    shop = 0

    def initialize_shop(self):
        """Fun to initialize a instance of Shop"""
        self.shop = classes.Shop(self.name)


class Registration(StatesGroup):
    reg = State()
    name = State()
    mail = State()
    key = State()


class Authorization(StatesGroup):
    aut = State()
    name = State()
    key = State()
    success = State()


class Shop(StatesGroup):
    name = State()
    shop = State()
    fun = State()
    arg1 = State()
    arg2 = State()
    arg3 = State()


class Verify(StatesGroup):
    key = State()
    email = State()


WEBHOOK_HOST = 'https://pmpu.site'
WEBHOOK_PATH = '/lecTop/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '127.0.0.1'
WEBAPP_PORT = 7787

# Объект бота
bot = Bot(token="6910863029:AAEd0EB4hvWTHef3mHPwFRUX0Ji8MUTMcJ0")

storage = MemoryStorage()
# storage = MongoStorage(host='localhost', port=27017, db_name='aiogram_fsm')
# dp = Dispatcher(bot, storage=storage)
# Диспетчер для бота
dp = Dispatcher(storage=storage)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

admin_id = []
user_id = []
photo_id = {"badges": [0, 0, 0, 0, 0, 0, 0], "pins": [0, 0], "stickers": [0, 0, 0],
            "covers": [0, 0, 0, 0, 0, 0], "pens": [0, 0, 0], "bracelets": [0], "notebooks": [0, 0, 0],
            "cups": [0, 0], "bottles": [0, 0], "thermal_mugs": [0], "t-shirts": [0, 0, 0, 0, 0, 0],
            "sweatshirts": [0], "sweaters": [0], "hoodie": [0], "gliders": [0]}
categories = []
translate = []
merch_with_size = []

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    global categories, photo_id, translate, merch_with_size
    df = pd.read_excel('merch.xlsx', header=0, index_col=0)
    photo_id = {list(df.index)[0][:-1]: [0]}
    categories = [list(df.index)[0][:-1]]
    df_ind = list(df.index)
    for i in range(1, len(df_ind)):
        flag = False
        categ = df_ind[i][:-1]
        if not categ.islower():
            categ = categ[:-1]
            flag = True
            if not categ.islower():
                categ = categ[:-1]
                if not categ.islower():
                    categ = categ[:-1]
        number = ""
        if categ[-1] in "0123456789":
            number = categ[-1]
            categ = categ[:-1]
            if categ[-1] in "0123456789":
                number = categ[-1] + number
                categ = categ[:-1]
                if categ[-1] in "0123456789":
                    number = categ[-1] + number
                    categ = categ[:-1]
        if flag:
            merch_with_size.append(categ+number)
        if categ not in categories:
            categories.append(categ)
            translate.append(list(df["ru"][i].split(" "))[0])
            photo_id[categ] = [0]
        else:
            photo_id[categ].append(0)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Регистрация",
        callback_data="registration")
    )
    builder.add(types.InlineKeyboardButton(
        text="Авторизация",
        callback_data="authorization")
    )
    await message.answer(
        "Добро пожаловать! Зайдите в свой аккаунт",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "registration")
async def registration(message: types.CallbackQuery, state: FSMContext):
    await message.message.answer("Введите ваше ФИО")
    await state.set_state(Registration.reg)


@dp.message(Registration.reg)
async def registration1(message: types.Message, state: FSMContext, bot: Bot):
    a = User()
    a.name = message.text
    await state.set_state(Registration.name)
    call_back = a.account.registration(a.name)
    builder1 = InlineKeyboardBuilder()
    builder1.add(types.InlineKeyboardButton(
        text="Авторизация",
        callback_data="authorization")
    )
    if call_back == 0:
        await message.reply("Тебе пришло письмо на почту. С этим кодом ты можешь авторизоваться!",
                            reply_markup=builder1.as_markup())
    elif call_back == 2:
        # ПОКА ПАСС. Тут ФИО совпадает.
        pass
    else:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отправить почту",
            callback_data="email " + str(call_back))
        )

        for adm in admin_id:
            await bot.send_message(adm, "Тут чувак новенький, в моих списках не значится. Проверь:"
                                   + a.name + ". Если все пучком, найди в тимсе почту, отправь её мне после нажатия на кнопочку",
                                   reply_markup=builder.as_markup())

        await message.reply(
            "Увы, мы не нашли тебя в наших списках. Админ посмотрит твою заявку и пришлет код на твою университетскую почту. Тогда ты и сможешь авторизоваться.",
            reply_markup=builder1.as_markup())


@dp.callback_query(EmailFilter(F.data))
async def give_email(message: types.CallbackQuery, state: FSMContext):
    await message.answer("Жду)")
    await state.set_state(Verify.email)
    await state.update_data(key=message.data.split(" ")[1])


@dp.message(Verify.email)
async def send_mail(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await state.clear()
    await classes.send_mail(message.text, user_data["key"])


@dp.callback_query(F.data == "authorization")
async def authorization(message: types.CallbackQuery, state: FSMContext):
    await message.message.answer("Введите ваше ФИО")
    await state.set_state(Authorization.name)


@dp.message(Authorization.name)
async def authorization1(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш пароль")
    await state.set_state(Authorization.key)


@dp.message(Authorization.key)
async def authorization2(message: types.Message, state: FSMContext):
    await state.update_data(key=message.text)
    a = classes.Account()
    user_data = await state.get_data()
    user = a.authorization(user_data['name'], user_data['key'])
    if user:
        await state.set_state(Shop.fun)
        await state.update_data(name=user)
        shop_instance = classes.Shop(name=user)
        await state.update_data(shop=shop_instance)
        if user == "Admin,PB,AMCP":
            # admin
            admin_id.append(message.chat.id)
            await message.answer(text="Выберите что поделать", reply_markup=make_row_keyboard(handlers.shop.admin_fun))

        else:
            await message.answer(text="Выберите что поделать", reply_markup=make_row_keyboard(handlers.shop.user_fun))
    else:
        await message.reply("Неверное ФИО или пароль")


@dp.message(F.text == "Меню")
async def menu(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await state.set_state(Shop.fun)
    if user_data['name'] == "Admin,PB,AMCP":
        # admin
        await message.answer(text="Выберите что поделать", reply_markup=make_row_keyboard(handlers.shop.admin_fun))
    else:
        await message.answer(text="Выберите что поделать", reply_markup=make_row_keyboard(handlers.shop.user_fun))


@dp.message(Shop.fun, F.text == handlers.shop.admin_fun[0])
async def print_dict(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(text=user_data["shop"].give_dict())
    await message.reply("В меню?", reply_markup=make_row_keyboard(["Меню"]))


@dp.message(F.text == handlers.shop.admin_fun[1], Shop.fun)
async def take_table_event(message: types.Message, state: FSMContext):
    await message.reply("Ну закинь табличку тогда в формате экселя")
    await state.set_state(Shop.arg1)
    await state.update_data(fun=handlers.shop.admin_fun[1])


@dp.message(Shop.arg1)
async def give_table_event(file: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    await bot.download(file.document, destination=f"/home/victor21/PycharmProjects/pbbot/files/1.xlsx")
    user_data["shop"].add_table_event(f"/home/victor21/PycharmProjects/pbbot/files/1.xlsx")
    await file.reply("Успешно! В меню?", reply_markup=make_row_keyboard(["Меню"]))


@dp.message(F.text == handlers.shop.admin_fun[2], Shop.fun)
async def take_points(message: types.Message, state: FSMContext):
    await message.reply("Ну напиши ФИО тогда и баллы через пробел (да-да и минусовые тоже)")
    await state.set_state(Shop.arg2)
    await state.update_data(fun=handlers.shop.admin_fun[2])


@dp.message(Shop.arg2)
async def change_points(message: types.message, state: FSMContext):
    user_data = await state.get_data()
    try:
        surname, name, patronymic, points = message.text.split(' ')
        user_data["shop"].change_points(surname + ',' + name + ',' + patronymic, points)
    except:
        surname, name, points = message.text.split(' ')
        user_data["shop"].change_points(surname + ',' + name, points)
    await message.reply("Успешно! В меню?", reply_markup=make_row_keyboard(["Меню"]))


@dp.message(F.text == handlers.shop.admin_fun[3], Shop.fun)
async def take_price(message: types.Message, state: FSMContext):
    await message.reply("Ну напиши че за мерч тогда и новую цену через пробел")
    await state.set_state(Shop.arg3)
    await state.update_data(fun=handlers.shop.admin_fun[4])


@dp.message(Shop.arg3)
async def change_price(message: types.message, state: FSMContext):
    user_data = await state.get_data()
    merch, points = message.text.split(' ')
    user_data["shop"].change_price(merch, points)
    await message.reply("Успешно! В меню?", reply_markup=make_row_keyboard(["Меню"]))


# TODO добавить и удалить мерч в самом конце делать


@dp.message(F.text == handlers.shop.user_fun[0], Shop.fun)
async def print_points(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(user_data["shop"].give_your_points())
    await message.reply("В меню?", reply_markup=make_row_keyboard(["Меню"]))


@dp.message(F.text == handlers.shop.user_fun[1], Shop.fun)
async def best_of_the_best(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    await message.answer(user_data["shop"].give_best())
    await message.reply("В меню?", reply_markup=make_row_keyboard(["Меню"]))


@dp.message(F.text == handlers.shop.user_fun[2], Shop.fun)
async def open_catalog(message: types.Message, state: FSMContext):
    global categories, translate
    # TODO Когда будет функция добавления категории запихнуть это все туда
    buttons = [[InlineKeyboardButton(text=translate[i], callback_data=categories[i]), InlineKeyboardButton(text=translate[i+1], callback_data=categories[i+1])] for i in range(0, len(categories), 2)]
    if len(categories) % 2 == 1:
        buttons.append([InlineKeyboardButton(text=translate[-1], callback_data=categories[1])])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Посмотри на наш ассортимент)", reply_markup=keyboard)


@dp.callback_query(F.data.in_(categories), Shop.fun)
async def open_merch(message: types.CallbackQuery, state: FSMContext):
    global photo_id
    # answer with all badges with photo and button to pay
    # TODO  ДЕЛАТЬ ОТСЮДА проверка на наличие товара, если нету то вместо купить писать нет в наличии
    user_data = await state.get_data()
    df = user_data["shop"].merch_dict
    for i in range(len(photo_id[message.data])):
        ind = list(df.index).index(message.data+'i')
        if ind == -1:
            ind = list(df.index).index(message.data + 'i'+"S")
            if ind == -1:
                ind = list(df.index).index(message.data + 'i' + "M")
                if ind == -1:
                    ind = list(df.index).index(message.data + 'i' + "L")
        if photo_id[message.data][i] == 0:
            image_from_pc = FSInputFile(f"catalog/{message.data}/{i+1}.jpg")
            result = await message.message.answer_photo(image_from_pc, caption=f"Тип {i+1}. Цена: не меньше{df['price'][ind]}",
                                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                                    InlineKeyboardButton(
                                                        text="Купить",
                                                        callback_data=f"confirm_{message.data}{i}")]]))
            photo_id[message.data][i] = result.photo[-1].file_id
        else:
            await message.message.answer_photo(photo_id[message.data][i], caption=f"Тип {i+1}. Цена: {df['price'][ind]}",
                                       reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                           [InlineKeyboardButton(text="Купить", callback_data=f"confirm_{message.data}{i}")]]))


@dp.callback_query(F.data.in_(merch_with_size), Shop.fun)
async def size_buy(message: types.CallbackQuery, state: FSMContext):
    merch = message.data[8:]
    user_data = await state.get_data()
    df = user_data["shop"].merch_dict
    start = 0
    j = 0
    for i in range(df.size[0]):
        if merch in list(df.index)[i]:
            j = i+1
            start = i
            while merch in list(df.index)[j]:
                j += 1
            break

    size = []
    for i in range(start, j):
        if df.iloc[i, 3] != "." and df.iloc[i, 2] > 0:
            size.append(list(df.index)[i].replace(merch, ""))

    markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=i, callback_data=f"confirm_{message.data}{i}") for i in size]])
    await message.message.answer("Выберите размер", reply_markup=markup)


@dp.callback_query(F.data.contains("confirm_"), Shop.fun)
async def confirm_buy(message: types.CallbackQuery):
    await message.message.answer("Вы уверены?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да!", callback_data=f"buy_{message.data[8:]}"),
            InlineKeyboardButton(text="Нет", callback_data="no")]
    ]))


@dp.callback_query(F.data.contains("buy_"), Shop.fun)
async def buy_merch(message: types.CallbackQuery, state: FSMContext, bot: Bot):
    merch = message.data[4:]
    user_data = await state.get_data()
    call_back = user_data["shop"].buy_merch(merch)
    if call_back == 0:
        for adm in admin_id:
            await bot.send_message(adm, "Тут " + user_data["name"] + " @"+message.from_user.username + " купил(а) "
                                   + user_data["shop"].merch_dict["ru"][merch] + ". Если все пучком, договорись, когда отдать")
        await message.message.answer('Все успешно. С вами свяжутся.')
    else:
        await message.message.answer('На вашем счете недостаточно средств. Кредитов мы не даем)')





# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запуск бота
    asyncio.run(main())
    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=WEBHOOK_PATH,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     skip_updates=True,
    #     host=WEBAPP_HOST,
    #     port=WEBAPP_PORT,
    #     )
