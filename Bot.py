import time_manager as main_functions
from visualizer import create_statistick
from config import *
from Api_token import *

import string
import random
import os
import asyncio
from services.database import dataBase

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ContentTypes, PreCheckoutQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from yoomoney import Quickpay, Client

storage = MemoryStorage()
PROXY_URL = "http://proxy.server:3128"
bot = Bot(API_TOKEN, proxy=PROXY_URL)
dispatcher = Dispatcher(bot, storage=storage)

cb = CallbackData("btn", "payment_type", "message_id")
db = dataBase(bd_user, bd_password, bd_host, bd_database)

class ClientStatesGroup(StatesGroup):
  Start = State()
  Wait = State()
  StartOptions = State()
  Recording_time = State()
  Recording_time_editmessage = State()
  Recording_employment = State()
  Getting_new_employment = State()
  Setting_new_employment = State()
  Deleteing_employment = State()
  payment_get_amount = State()
  payment = State()

# ===================================КЛАВИАТУРА====================================
# Функция для применения клавы:
def getKeyboard(keyboardButtons, mode=1) -> ReplyKeyboardMarkup:
  keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
  if mode == 1:
    keyboard.add(keyboardButtons)
  else:
    for button in keyboardButtons:
      keyboard.add(button)
  return keyboard

# Функция для удаления клавы:
def removeKeyboard() -> ReplyKeyboardRemove:
  return ReplyKeyboardRemove(True)

# INLINE KEYBOARD:
def setInlineKeyboard(InlineKeyboardButtons, mode=1) -> InlineKeyboardMarkup:
  keyboard = InlineKeyboardMarkup()
  if mode == 3:
    keyboard = InlineKeyboardMarkup(inline_keyboard=InlineKeyboardButtons)
    return keyboard
  if mode == 1:
    keyboard.add(InlineKeyboardButtons)
  elif mode == 2:
    for inlineButton in InlineKeyboardButtons:
      keyboard.add(inlineButton)
  return keyboard
# =================================================================================



# =============================ОБРАБОТЧИКИ КОМАНД БОТА=============================

# Режим разработчика
isDevelopment = False
# isDevelopment = True
# bot = Bot(API_DEVELOPMENT_TOKEN)
# dispatcher = Dispatcher(bot, storage=storage)
# Режим разработчика

#==============================MONEY==============================#
#================TG OFFICIAL================#
@dispatcher.pre_checkout_query_handler(lambda q: True, state="*")
async def pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
  await ClientStatesGroup.Wait.set()
  print("PRE_CHECKOUT_PAYMANT")
  await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
  return await ClientStatesGroup.Start.set()

@dispatcher.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT, state="*")
async def seccessful_payment(message: types.Message):
  total_amount = message.successful_payment.total_amount / 100
  if os.path.exists("./data/donaters.txt"):
    with open("./data/donaters.txt", "a", encoding="UTF-8-sig") as file:
      file.write(f"\nfull_name:\"{message.from_user.full_name}\", id:{message.from_user.id}, username:\"{message.from_user.username}\", full_summ:{total_amount}")
  await message.answer(text="Спасибо за поддержку! Благодаря вам я буду дальше развивать данный проект, чтобы им было еще комфортнее пользоваться!")
  await asyncio.sleep(1)
  return await bot.send_sticker(chat_id=message.from_user.id, sticker="CAACAgIAAxkBAAEIvzdkSjBDufLgkvRK8sdtE7OmgrAv5QACchIAAkblqUjyTBtFPtcDUS8E")
#================TG OFFICIAL================#

#================YOOMONEY===================#
#================YOOMONEY===================#

#==============================MONEY==============================#

# Режим разработчика
# @dispatcher.message_handler(lambda message: message.from_user.id != ADMIN_ID)
# async def allert(message: types.Message):
#   with open("./data/blacklist.txt", "r") as file:
#     data = file.readlines()
#     for line in data:
#       if line == "\n":
#         continue
#       elif line.strip() == str(message.from_user.id):
#         return
#   await message.answer('Бот сейчас находится на технической паузе. Извините за неудобства!')
#   with open("./data/blacklist.txt", "a") as file:
#     file.write(f"\n{message.from_user.id}")
#   await message.answer("Если у вас возникли какие-либо сложности, напишите создателю бота: https://t.me/At1set", )
# Режим разработчика



@dispatcher.message_handler(lambda message: message.text != "/start", state=[None])
async def hello(message: types.Message):
  if not isDevelopment:
    await message.answer('Для того, чтобы начать, введи:\n/start')
  else:
    return await ClientStatesGroup.Start.set()

@dispatcher.message_handler(lambda message: message.text != "/exit", state=[ClientStatesGroup.Wait, ClientStatesGroup.Setting_new_employment, ClientStatesGroup.Recording_employment, ClientStatesGroup.Deleteing_employment, ClientStatesGroup.payment])
async def waiting(message: types.Message):
  await message.delete()

@dispatcher.message_handler(commands=["start"], state=None)
async def start(message: types.Message):
  await ClientStatesGroup.Wait.set()
  # KeyboardButtons:
  InlineKeyboardButtons = InlineKeyboardButton("Продолжить", callback_data="start_continue")

  await bot.send_sticker(chat_id=message.from_user.id, sticker="CAACAgIAAxkBAAEIqv9kQluv7HY9Ece-TGQ8Fmioal803gACKgMAAs-71A4f8rUYf2WfMC8E")
  await asyncio.sleep(1)
  await message.answer(f"Привет {message.from_user.full_name}!\nДобро пожаловать в моего бота <b>Time manager</b>⏰", parse_mode="HTML")
  await asyncio.sleep(1.5)
  await bot.send_message(message.from_user.id, text=MESSAGE__HI, parse_mode="HTML",
                        reply_markup=setInlineKeyboard(InlineKeyboardButtons))
  await main_functions.write_data(message.from_user.id)
  await ClientStatesGroup.Start.set()

@dispatcher.message_handler(commands=["help", "menu", "about", "info", "info_1", "info_2", "info_3", "info_4", "info_5", "info_6", "info_7", "start_task_recording", "options", "donate"], state=[ClientStatesGroup.Start, ClientStatesGroup.Wait, ClientStatesGroup.Recording_time, ClientStatesGroup.Recording_employment, ClientStatesGroup.Getting_new_employment, ClientStatesGroup.Setting_new_employment, ClientStatesGroup.Deleteing_employment])
async def commands(message: types.Message, state: FSMContext):
  if message.text == "/start_task_recording" or message.text == "/options" or message.text == "/help":
    curr_state = await state.get_state()

  if message.text == "/menu":
    await bot.send_message(message.from_user.id, text=MESSAGE__MAIN_MENU, parse_mode="HTML")

  elif message.text == "/help":
    await ClientStatesGroup.Wait.set()
    await bot.send_message(message.from_user.id, text=MESSAGE__HELP_1, parse_mode="HTML")
    await bot.send_photo(chat_id=message.from_user.id, photo=types.InputFile(f"./data/default/images/employments_list.png"))
    await bot.send_message(message.from_user.id, text=MESSAGE__HELP_2, parse_mode="HTML")
    await bot.send_message(message.from_user.id, text=MESSAGE__HELP_3, parse_mode="HTML")
    await asyncio.sleep(5)
    await bot.send_message(message.from_user.id, text=MESSAGE__HELP_4, parse_mode="HTML")
    await state.set_state(curr_state)

  elif message.text == "/about":
    await bot.send_message(message.from_user.id, text=MESSAGE__ABOUT, parse_mode="HTML")

  elif message.text == "/info" or "/info" in message.text:
    if message.text == "/info":
      result_message, count_days = await main_functions.get_day_info(message.from_user.id)
      if result_message == False and count_days == False:
        await message.answer(text="Невозможно показать статистику, так как у меня отсутствуют ваши данные!")
        return
      if count_days == 1:
        await message.answer(text=f"Ваша статистика за сегодня:\n{result_message}")
        isCreated = await create_statistick(message.from_user.id)
        if isCreated:
          await bot.send_photo(chat_id=message.from_user.id, photo=types.InputFile(f"data/users/{message.from_user.id}/Temp/statistic.jpg"))
      else:
        more_info_message = ""
        for i in range(count_days-1, 0, -1):
          if i + 1 == count_days:
            more_info_message += f"\nПоказать статистику за прошлый день:\n/info_{i}\n"
          elif i + 2 == count_days:
            more_info_message += f"\nПоказать статистику за позапрошлый день:\n/info_{i}\n"
          else:
            more_info_message += f"\nПоказать статистику за {i} день:\n/info_{i}\n"
        await message.answer(text=f"Ваша статистика за сегодня:\n{result_message}")
        isCreated = await create_statistick(message.from_user.id)
        if isCreated:
          await bot.send_photo(chat_id=message.from_user.id, photo=types.InputFile(f"data/users/{message.from_user.id}/Temp/statistic.jpg"))
        await asyncio.sleep(1)
        await message.answer(text=f"Также вам доступна статистика за прошедшие дни:\n{more_info_message}")
    else:
      if not "_" in message.text:
        return await message.answer(text="Некорректная форма записи /info!\nСинтаксис (правильное написание) данной команды вы можете посмотреть:\n/help")
      curr_day = int(message.text.split("_")[1].strip())
      result_message, count_days = await main_functions.get_day_info(message.from_user.id, curr_day)
      if result_message == False and count_days == False:
        await message.answer(text="Невозможно показать статистику, так как у меня отсутствуют ваши данные!")
        return
      more_info_message = ""
      for i in range(count_days-1, 0, -1):
        if i == curr_day:
          continue
        if i + 1 == count_days:
          more_info_message += f"\nПоказать статистику за прошлый день:\n/info_{i}\n"
        elif i + 2 == count_days:
          more_info_message += f"\nПоказать статистику за позапрошлый день:\n/info_{i}\n"
        else:
          more_info_message += f"\nПоказать статистику за {i} день:\n/info_{i}\n"

      if count_days == curr_day:
        await message.answer(text=f"Ваша статистика за сегодня:\n{result_message}")
        if more_info_message != "":
          await asyncio.sleep(0.5)
          await message.answer(text=f"Также вам доступна статистика за другие дни:\n{more_info_message}")
      elif count_days-1 == curr_day:
        await message.answer(text=f"Ваша статистика за вчера:\n{result_message}")
        if more_info_message != "":
          await asyncio.sleep(0.5)
          await message.answer(text=f"Также вам доступна статистика за другие дни:\n{more_info_message}")
      elif count_days-2 == curr_day:
        await message.answer(text=f"Ваша статистика за позавчера:\n{result_message}")
        if more_info_message != "":
          await asyncio.sleep(0.5)
          await message.answer(text=f"Также вам доступна статистика за другие дни:\n{more_info_message}")
      else:
        await message.answer(text=f"Ваша статистика за {curr_day} день записи:\n{result_message}")
        if more_info_message != "":
          await asyncio.sleep(0.5)
          await message.answer(text=f"Также вам доступна статистика за другие дни:\n{more_info_message}")

  elif (message.text == "/start_task_recording"):
    if curr_state != "ClientStatesGroup:Recording_time":
      # отправляем сообщение
      await ClientStatesGroup.Wait.set()
      await main_functions.animate_message_loading(bot=bot, message=message, text="Включаю режим записи")
      await bot.send_message(message.from_user.id, text=MESSAGE__START_TIME_RECORDING, parse_mode="HTML")
      # Получаем кнопки конкретного пользователя
      keyboardButtons = await main_functions.get_employment_list(message.from_user.id)
      # await ClientStatesGroup.Wait.set() Удалил, хз зачем оно тут
      await asyncio.sleep(0.5)
      asyncio.create_task(main_functions.animate_message_loading(bot=bot, message=message, text="Получение списка дел", count=3))
      await asyncio.sleep(5.5)
      await bot.send_message(message.from_user.id, text="Ожидание ввода...", reply_markup=getKeyboard(keyboardButtons, mode=2))
      await asyncio.sleep(0.5)
      await ClientStatesGroup.Recording_time.set()
    else:
      await ClientStatesGroup.Wait.set()
      await asyncio.sleep(0.5)
      await message.answer('Запись уже ведется!', reply_markup=removeKeyboard())
      await asyncio.sleep(1)
      await bot.send_message(message.from_user.id, text=MESSAGE__START_TIME_RECORDING, parse_mode="HTML")
      await asyncio.sleep(1)
      await message.answer('Для этого удобно использовать всплывающую клавиатуру снизу ввода.')
      keyboardButtons = await main_functions.get_employment_list(message.from_user.id)
      await bot.send_message(message.from_user.id, text="Ожидание ввода...", reply_markup=getKeyboard(keyboardButtons, mode=2))
      await ClientStatesGroup.Recording_time.set()

  elif (message.text == "/options"):
    if curr_state != "ClientStatesGroup:Recording_time":
      await ClientStatesGroup.StartOptions.set()
      await bot.send_message(message.from_user.id, text=MESSAGE__OPTIONS, parse_mode="HTML", reply_markup=setInlineKeyboard(InlineKeyboardButtons=InlineKeyboardButton("Закрыть", callback_data=message.message_id)))
    else:
      await message.answer(text="Меню настроек нельзя вызывать в режиме записи. Если вам надо открыть настройки, выйдите из режима зависи с помощью:\n/exit")

  elif (message.text == "/donate"):
    await ClientStatesGroup.payment.set()
    
    await message.answer(text="Пожалуйста, выберите способ оплаты", reply_markup=setInlineKeyboard(InlineKeyboardButtons=[
                                                                        # InlineKeyboardButton(text="QIWI 🥝", callback_data="QIWI"),
                                                                        InlineKeyboardButton(text="ЮMoney 👾", callback_data=f"btn:ЮMoney:{message.message_id}"),
                                                                        InlineKeyboardButton(text="Картой 💳", callback_data=f"btn:Card:"),
                                                                        InlineKeyboardButton(text="Отмена", callback_data=f"btn:exit:{message.message_id}")
                                                                        ],
                                                                        mode=2))
    return

    # return await message.answer(text="Пожалуйста, выберите размер платежа.", reply_markup=setInlineKeyboard(InlineKeyboardButtons=[InlineKeyboardButton(text="Поддержать разработчика (100 руб.)", callback_data="100"),
    #                                                                     InlineKeyboardButton(text="Мега поддержать разработчика (250 руб.)", callback_data="250"),
    #                                                                     InlineKeyboardButton(text="Ультра поддержать разработчика (500 руб.)", callback_data="500"),
    #                                                                     InlineKeyboardButton(text="Отмена", callback_data=f"exit-{message.message_id}")],
    #                                                                     mode=2))

@dispatcher.message_handler(state=ClientStatesGroup.payment_get_amount)
async def set_payment_amount(message: types.Message, state: FSMContext):
  await ClientStatesGroup.Wait.set()
  amount = message.text.strip()
  try:
    if not "," in amount:
      amount = int(amount)
    if "." in message.text or "," in message.text:
      await message.delete()
      message = await message.answer("Сумма должна быть целой!")
      await asyncio.sleep(3)
      await message.delete()
      return await ClientStatesGroup.payment_get_amount.set()
    if amount >= 15000:
      await message.delete()
      message = await message.answer("Ого, да вы богач! Но, к сожалению, сумма не должна быть столь большой (максимальная: 14 999)!")
      await asyncio.sleep(3)
      await message.delete()
      return await ClientStatesGroup.payment_get_amount.set()
    if amount < 25:
      await message.delete()
      message = await message.answer("К сожалению, минимальная сумма не должна быть меньше 25 рублей!")
      await asyncio.sleep(3)
      await message.delete()
      return await ClientStatesGroup.payment_get_amount.set()
  except:
    await message.delete()
    message = await message.answer(text=f'\"{message.text}\" не является числом! Пожалуйста, выберите сумму с помощью кнопок или же введите чилсо корректно.')
    await asyncio.sleep(3)
    await message.delete()
    return await ClientStatesGroup.payment_get_amount.set()
  
  # Удаляем сообщение с ценой
  await message.delete()

  # Удаляем сообщение с кнопками выбора цены
  inline_message_id = await state.get_data("inline_message_id")
  inline_message_id = inline_message_id["inline_message_id"]
  chat_id = message.from_user.id
  await bot.delete_message(chat_id=chat_id, message_id=inline_message_id)

  letters_and_digits = string.ascii_lowercase + string.digits
  rand_string = f"{message.from_user.id}".join(random.sample(letters_and_digits, 10))
  rand_string = "".join(random.sample(letters_and_digits, 10))

  quickpay = Quickpay(
    receiver='4100118185732942',
    quickpay_form='shop',
    targets='@At1sets_TimeManager_bot',
    paymentType='SB',
    sum=amount,
    label=rand_string
  )

  await db.add_user(user_id=message.from_user.id, name=message.from_user.full_name)
  await db.update_label(user_id=chat_id, label=rand_string)
  await bot.send_message(chat_id=chat_id, text="Готово, теперь вы можете оплатить по ссылке ниже! После оплаты, нажмите на кнопку \"Завершить олату\"", reply_markup=setInlineKeyboard(
    InlineKeyboardButtons=[InlineKeyboardButton(text="Открыть форму", url=quickpay.redirected_url),
                           InlineKeyboardButton(text="Завершить олату", callback_data="claim")],
  mode=2))
  await state.reset_data()
  await state.set_data({"total_amount": amount})
  return await ClientStatesGroup.payment.set()

@dispatcher.message_handler(state=ClientStatesGroup.StartOptions)
async def starting_options(message: types.Message):
  if message.text == "/default_employment_list":
    await message.delete()
    await ClientStatesGroup.Wait.set()
    # получаем значение
    user_properties = main_functions.UserProperties(user_id=message.from_user.id, default_value=1)
    property_value = await user_properties.get("default_employment_list")
    # меняем на противоположное
    property_value = 0 if property_value == 1 else 1
    user_properties = main_functions.UserProperties(user_id=message.from_user.id, default_value=property_value)
    await user_properties.set("default_employment_list")
    if property_value == 1:
      _message = await message.answer(text="Вы включили показ стандартного списка дел!")
    else:
      _message = await message.answer(text="Вы отключили показ стандартного списка дел!")
    await asyncio.sleep(2)
    await _message.delete()
    return await ClientStatesGroup.StartOptions.set()
  else:
    return await message.delete()

@dispatcher.message_handler(lambda message: not "/" in message.text, state=[ClientStatesGroup.Recording_time, ClientStatesGroup.Recording_time_editmessage])
async def choice_employment(message: types.Message, state: FSMContext):
  curr_state = await state.get_state()
  isMessageEdit = curr_state == "ClientStatesGroup:Recording_time_editmessage"
  await ClientStatesGroup.Recording_employment.set()
  employment = message.text
  _message = await message.answer(text=f'Начата запись: \n{employment}', reply_markup=setInlineKeyboard([InlineKeyboardButton(text='Изменить ⚙️', callback_data=message.message_id),
                                                                                                         InlineKeyboardButton(text='Отмена ⛔️', callback_data=f"exit-{message.message_id}"),
                                                                                                         InlineKeyboardButton(text='Закончить ✅', callback_data="break")],
                                                                                                         mode=2))
  await main_functions.startRecording(user_id=message.from_user.id, employment=employment, isMessageEdit=isMessageEdit)
  data = {"buffer_inline_message": _message}
  await state.set_data(data)

@dispatcher.message_handler(commands=["set_new_employment"], state=[ClientStatesGroup.Recording_time])
async def getting_new_employment_change_state(message: types.Message, state: FSMContext):
  await ClientStatesGroup.Getting_new_employment.set()
  _message = await message.answer(text='Введите новое занятие, для добавления его в список', reply_markup=setInlineKeyboard(InlineKeyboardButton(text='Отмена', callback_data=message.message_id)))
  await state.set_data({"buffer_command_message": message, "buffer_inline_message": _message})
  _message = await message.answer(text='Удаление клавиатуры...', reply_markup=removeKeyboard())
  await asyncio.sleep(0.1)
  await _message.delete()

@dispatcher.message_handler(state=ClientStatesGroup.Getting_new_employment)
async def getting_new_employment(message: types.Message, state: FSMContext):
  incorrect_symbols = ["_", "-", "/", "\\"] 
  if message.text == "/incorrect_symbols":
    # Удаляем сообщение с inline кнопкой "отмена" и пересылаем его обратно:
    chat_id = message.from_user.id
    data = await state.get_data("buffer_inline_message")
    inline_message_id = data["buffer_inline_message"]["message_id"]
    data = await state.get_data("buffer_command_message")
    command_message = data["buffer_command_message"]
    command_message_id = data["buffer_command_message"]["message_id"]
    await bot.delete_message(chat_id=chat_id, message_id=inline_message_id)
    # =========
    message_answer = ""
    for symbol in incorrect_symbols:
      message_answer += f"\"{symbol}\" "
    await message.answer(text=f"Символы, которые запрещены в названии:\n{message_answer}")
    # Пересылаем обратно сообщение с inline кнопкой "отмена", после всего контента
    _message = await message.answer(text='Введите новое занятие, для добавления его в список', reply_markup=setInlineKeyboard(InlineKeyboardButton(text='Отмена', callback_data=command_message_id)))
    return await state.set_data({"buffer_command_message": command_message, "buffer_inline_message": _message})
    # =========
  for symbol in incorrect_symbols:
    if symbol in message.text:
      # Удаляем сообщение с inline кнопкой "отмена" и пересылаем его обратно:
      chat_id = message.from_user.id
      data = await state.get_data("buffer_inline_message")
      inline_message_id = data["buffer_inline_message"]["message_id"]
      data = await state.get_data("buffer_command_message")
      command_message = data["buffer_command_message"]
      command_message_id = data["buffer_command_message"]["message_id"]
      await bot.delete_message(chat_id=chat_id, message_id=inline_message_id)
      # =========
      await asyncio.sleep(0.5)
      await message.answer(text=f"Ваше занятие включает такой недопустимый символ, как: \"{symbol}\"")
      await asyncio.sleep(0.5)
      await message.answer(text=f"Пожалуйста перефразируйте название вашего вида занятия, без использования недопустимого символа!\n\nСписок запрещенных символов в названии рода деятельности, можно с помощью команды:\n/incorrect_symbols")
      # Пересылаем обратно сообщение с inline кнопкой "отмена", после всего контента
      _message = await message.answer(text='Введите новое занятие, для добавления его в список', reply_markup=setInlineKeyboard(InlineKeyboardButton(text='Отмена', callback_data=command_message_id)))
      return await state.set_data({"buffer_command_message": command_message, "buffer_inline_message": _message})
  await ClientStatesGroup.Setting_new_employment.set()
  data = await state.get_data("current_message")
  data["current_message"] = message
  await state.set_data(data)
  await message.answer(text=f"Добавить \"{message.text}\" в список дел?", reply_markup=setInlineKeyboard([InlineKeyboardButton(text='Изменить', callback_data=message.message_id),
                                                                                              InlineKeyboardButton(text='Добавить', callback_data="add")],
                                                                                              mode=2))

@dispatcher.message_handler(commands=["delete_employment"], state=[ClientStatesGroup.Recording_time])
async def delete_employment(message: types.Message):
  await ClientStatesGroup.Deleteing_employment.set()
  InlineKeyboardButtons = await main_functions.get_employment_list(user_id=message.from_user.id, mode=2)
  if InlineKeyboardButtons:
    InlineKeyboardButtons.append(InlineKeyboardButton(text="Отмена", callback_data=f"break-{message.message_id}"))
    await message.answer(text="Выберите нужную запись для удаления", reply_markup=setInlineKeyboard(InlineKeyboardButtons, mode=2))
    _message = await message.answer(text='Удаление клавиатуры...', reply_markup=removeKeyboard())
    await asyncio.sleep(0.1)
    await _message.delete()
  else:
    await message.answer(text="Ваш собственный список дел пуст.\n\nОднако, вы можете пополнить его:\n/set_new_employment")
    await asyncio.sleep(2)
    await message.answer(text="Ожидание ввода...")
    await ClientStatesGroup.Recording_time.set()
# =================================================================================


# ===============================ОБРАБОТЧИК ВЫХОДОВ================================
@dispatcher.message_handler(commands=["exit"], state=[ClientStatesGroup.Recording_time, ClientStatesGroup.Start, ClientStatesGroup.StartOptions, ClientStatesGroup.payment])
async def exit_from_state(message: types.Message, state: FSMContext):
  curr_state = await state.get_state()
  await message.delete()
  if curr_state == "ClientStatesGroup:Recording_time" or curr_state == "ClientStatesGroup:Recording_time":
    await ClientStatesGroup.Wait.set()
    _message = await bot.send_message(message.from_user.id, text='Вы вышли из режима записи.', reply_markup=removeKeyboard())
    await asyncio.sleep(2)
    await _message.delete()
    await asyncio.sleep(0.5)
    await bot.send_message(message.from_user.id, text=MESSAGE__MAIN_MENU, parse_mode="HTML")
    return await ClientStatesGroup.Start.set()
  _message = await bot.send_message(message.from_user.id, text='Выход.', reply_markup=removeKeyboard())
  await asyncio.sleep(1)
  await _message.delete()
  return await state.finish()
# =================================================================================

@dispatcher.callback_query_handler(lambda callback: callback.data == "start_continue", state="*")
async def callback_onStart(callback: types.CallbackQuery):
  await bot.send_message(callback.from_user.id, text=MESSAGE__MAIN_MENU, parse_mode="HTML")
  await bot.answer_callback_query(callback.id)

@dispatcher.callback_query_handler(state=[ClientStatesGroup.StartOptions])
async def callback_onStart(callback: types.CallbackQuery):
  # Удаление сообщения с inline-кнопкой
  chat_id = callback.message.chat.id
  message_id = callback.message.message_id
  await bot.delete_message(chat_id, message_id)
  
  # Удаление сообщения с командой
  message_id = callback.data
  await bot.delete_message(chat_id, message_id)
  return await ClientStatesGroup.Start.set()


@dispatcher.callback_query_handler(state=ClientStatesGroup.Getting_new_employment)
async def callback_onGetting_new_employment(callback: types.CallbackQuery):
  # Удаление сообщения с inline-кнопкой
  chat_id = callback.message.chat.id
  message_id = callback.message.message_id
  await bot.delete_message(chat_id, message_id)

  # Удаление сообщения с командой
  message_id = callback.data
  await bot.delete_message(chat_id, message_id)
  keyboardButtons = await main_functions.get_employment_list(callback.from_user.id)
  await asyncio.sleep(2)
  await bot.send_message(callback.from_user.id, text="Ожидание ввода...", reply_markup=getKeyboard(keyboardButtons, mode=2))
  return await ClientStatesGroup.Recording_time.set()
  

@dispatcher.callback_query_handler(state=ClientStatesGroup.Setting_new_employment)
async def callback_onSetting_new_employment(callback: types.CallbackQuery, state: FSMContext):
  if callback.data == "add":
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    data = await state.get_data("current_message")
    current_message =  data["current_message"]["text"]

    # Изменение сообщения "Введите новое занятие, для добавления его в список"
    data = await state.get_data("buffer_inline_message")
    inline_message_id = data["buffer_inline_message"]["message_id"]
    await bot.edit_message_text("Введите новое имя занятия, для добавления его в список",
                                message_id=inline_message_id,
                                chat_id=callback.from_user.id)

    is_repeat_employment = await main_functions.set_new_employment(user_id=callback.from_user.id, employment=current_message)
    if is_repeat_employment:
      await bot.edit_message_text(text=f"Данное занятие уже находится в вашем списке!", message_id=message_id, chat_id=chat_id)
    else:
      await bot.edit_message_text(text=f"Занятие \"{current_message}\" было добавлено в список ваших дел!\n{MESSAGE__SET_NEW_EMPLOYMENT}",
                                  message_id=message_id,
                                  chat_id=chat_id,
                                  parse_mode="HTML")
    await state.reset_data()
    keyboardButtons = await main_functions.get_employment_list(callback.from_user.id)
    await bot.send_message(callback.from_user.id, text="Ожидание ввода...", reply_markup=getKeyboard(keyboardButtons, mode=2))
    return await ClientStatesGroup.Recording_time.set()
  
  elif callback["message"]["reply_markup"]["inline_keyboard"][0][0]["text"] != "Отмена":
    # Удаление сообщения с inline-кнопкой
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.delete_message(chat_id, message_id)

    # Удаление изменяемого сообщения
    data = await state.get_data("current_message")
    current_message =  data["current_message"]
    current_message_id = current_message["message_id"]
    await bot.delete_message(chat_id, current_message_id)

    return await ClientStatesGroup.Getting_new_employment.set()
  else:
    return

@dispatcher.callback_query_handler(state=ClientStatesGroup.Recording_employment)
async def callback_onRecording_employment(callback: types.CallbackQuery, state: FSMContext):

  if callback.data == "break":
    chat_id = callback.message.chat.id
    data = await state.get_data("buffer_inline_message")
    inline_message_id = data["buffer_inline_message"]["message_id"]
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=inline_message_id, reply_markup=None)
    time_interval = await main_functions.stopRecording(user_id=chat_id)
    if time_interval:
      time_difference = await main_functions.calc_time(time_interval)
      await bot.send_message(chat_id=chat_id, text=f"Дело завершено!\nВремя, затраченное на него у вас составило: {time_difference}")
    else:
      await bot.send_message(chat_id=chat_id, text="Странно хмм..., но, видимо, данное действие было уже завершено. Непридвиденная ошибка.")
    await asyncio.sleep(2)
    await bot.send_message(chat_id=chat_id, text="Ожидание ввода...")
    return await ClientStatesGroup.Recording_time.set()
  elif "exit" in callback.data:
    await main_functions.delete_employment_from_recording(callback.message.chat.id)
    # Удаление сообщения с inline-кнопкой
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.delete_message(chat_id, message_id)

    # Удаление сообщения с командой
    message_id = callback.data.split("-")[1]
    await bot.delete_message(chat_id, message_id)
    return await ClientStatesGroup.Recording_time.set()
  else:
    # Удаление сообщения с inline-кнопкой
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.delete_message(chat_id, message_id)

    # Удаление сообщения с командой
    message_id = callback.data
    await bot.delete_message(chat_id, message_id)
    return await ClientStatesGroup.Recording_time_editmessage.set()

@dispatcher.callback_query_handler(state=ClientStatesGroup.Deleteing_employment)
async def callback_onDeleteing_employment(callback: types.CallbackQuery):
  callback_button, callback_message = callback.data.split("-")
  if callback_button == "break":
    # Удаление сообщения с inline-кнопкой
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.delete_message(chat_id, message_id)

    # Удаление сообщения с командой
    await bot.delete_message(chat_id, callback_message)
    keyboardButtons = await main_functions.get_employment_list(callback.from_user.id)
    await bot.send_message(callback.from_user.id, text="Ожидание ввода...", reply_markup=getKeyboard(keyboardButtons, mode=2))
    return await ClientStatesGroup.Recording_time.set()
  else:
    chat_id = callback.message.chat.id
    inline_message_id = callback.message.message_id
    await main_functions.delete_employment_from_list(user_id=chat_id, employment=callback_message)
    await bot.edit_message_text(message_id=inline_message_id, chat_id=chat_id, text=f"Занятие \"{callback_message}\" было удалено из вашего списка!")
    keyboardButtons = await main_functions.get_employment_list(callback.from_user.id)
    await asyncio.sleep(2)
    await bot.send_message(chat_id=callback.from_user.id, text="Ожидание ввода...", reply_markup=getKeyboard(keyboardButtons, mode=2))
    return await ClientStatesGroup.Recording_time.set()

@dispatcher.callback_query_handler(cb.filter(payment_type=['ЮMoney', 'Card', 'exit', "left_fast", "left_slow", "pass", "right_slow", "right_fast"]), state=[ClientStatesGroup.payment_get_amount, ClientStatesGroup.payment])
async def callback_onGetPAymentAmount(callback: types.CallbackQuery, state: FSMContext):
  curr_state = await state.get_state()
  if curr_state == "ClientStatesGroup:payment":
    await ClientStatesGroup.payment_get_amount.set()

  prefix, payment_type, command_message_id = cb.parse(callback_data=callback.data).values()
  chat_id = callback.from_user.id

  if payment_type == "exit":
    # Удаление сообщения с inline-кнопкой
    message_id = callback.message.message_id
    await bot.delete_message(chat_id, message_id)

    # Удаление сообщения с командой
    await bot.delete_message(chat_id, command_message_id)

    await ClientStatesGroup.Start.set()
    return await callback.answer('')

  elif payment_type == "Card":
    return await callback.answer("Извините, но в данный момент оплата картой не поддерживается! Пожалуйста, выберете другой способ оплаты.", show_alert=True)
  
  elif payment_type == "ЮMoney":
    await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
    inline_message_id = await bot.send_message(chat_id=chat_id, text="А теперь выберите или введите сумму сами.\n(минимальная сумма 25 рублей)",
                           reply_markup=setInlineKeyboard(InlineKeyboardButtons=[
                             [InlineKeyboardButton(text='⏪', callback_data=f'btn:left_fast:25-{command_message_id}'), InlineKeyboardButton(text='◀️', callback_data=f'btn:left_slow:25-{command_message_id}'), InlineKeyboardButton(text='25', callback_data=f'btn:pass:25-{command_message_id}'), InlineKeyboardButton(text='▶️', callback_data=f'btn:right_slow:25-{command_message_id}'), InlineKeyboardButton(text='⏩', callback_data=f'btn:right_fast:25-{command_message_id}')],
                             [InlineKeyboardButton(text="Подтвердить", callback_data=f"btn:continue:{command_message_id}")],
                             [InlineKeyboardButton(text="Отмена", callback_data=f"btn:exit:{command_message_id}")]
                           ], mode=3))
    await state.set_data({"inline_message_id": inline_message_id.message_id})
  
  elif payment_type == "left_fast" or payment_type == "left_slow" or payment_type == "pass" or payment_type == "right_slow" or payment_type == "right_fast":
    amount, command_message_id = command_message_id.split('-')
    amount = int(amount)
    if payment_type == "pass":
      return await callback.answer('')
    if payment_type == "left_fast":
      if amount > 50:
        amount -= 50
      else:
        return await callback.answer('')
    elif payment_type == "left_slow":
      if amount > 25:
        amount -= 25
      else:
        return await callback.answer('')
    elif payment_type == "right_fast":
      amount += 50
    elif payment_type == "right_slow":
      amount += 25

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=callback.message.message_id,
                           reply_markup=setInlineKeyboard(InlineKeyboardButtons=[
                             [InlineKeyboardButton(text='⏪', callback_data=f'btn:left_fast:{amount}-{command_message_id}'), InlineKeyboardButton(text='◀️', callback_data=f'btn:left_slow:{amount}-{command_message_id}'), InlineKeyboardButton(text=f'{amount}', callback_data=f'btn:pass:{amount}-{command_message_id}'), InlineKeyboardButton(text='▶️', callback_data=f'btn:right_slow:{amount}-{command_message_id}'), InlineKeyboardButton(text='⏩', callback_data=f'btn:right_fast:{amount}-{command_message_id}')],
                             [InlineKeyboardButton(text="Подтвердить", callback_data=f"btn:continue:{amount}")],
                             [InlineKeyboardButton(text="Отмена", callback_data=f"btn:exit:{command_message_id}")]
                           ], mode=3))
    return await callback.answer('')

@dispatcher.callback_query_handler(state=[ClientStatesGroup.payment, ClientStatesGroup.payment_get_amount])
async def callback_onPayment(callback: types.CallbackQuery, state: FSMContext):
  curr_state = await state.get_state()
  isInit = False
  if curr_state == "ClientStatesGroup:payment_get_amount":
    prefix, data, amount = cb.parse(callback_data=callback.data).values()
    if data == "continue":
      await ClientStatesGroup.payment.set()
      await state.set_data({"total_amount": amount})
      await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
      isInit = True

  if callback.data == "quit":
    # Удаление сообщения с inline-кнопкой
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.delete_message(chat_id, message_id)

    await db.update_label(user_id=chat_id, label=1)
    return await ClientStatesGroup.Start.set()

  elif callback.data == "Card":
    pass
    # price = int(callback.data)
    # if price == 100:
    #   price_label = "Поддержать разработчика"
    # elif price == 250:
    #   price_label = "Мега поддержать разработчика"
    # else:
    #   price_label = "Ультра поддержать разработчика"
    # chat_id = callback.message.chat.id
    # PPRICE = types.LabeledPrice(label=price_label, amount=100*price)
    # print(price, PPRICE)
    # return await bot.send_invoice(
    #   chat_id=chat_id,
    #   title=price_label,
    #   description="Мяу",
    #   provider_token=API_YOOKASSA_PAYMENT_TEST,
    #   currency="RUB",
    #   photo_url="https://i.pinimg.com/736x/f4/d2/96/f4d2961b652880be432fb9580891ed62.jpg",
    #   photo_width=736,
    #   photo_height=734,
    #   photo_size=736,
    #   is_flexible=False,
    #   prices=[PPRICE],
    #   start_parameter="support-payment",
    #   payload="support-payment")

  elif callback.data == "ЮMoney" or callback.data == "back_to_payment" or isInit:
    letters_and_digits = string.ascii_lowercase + string.digits
    rand_string = f"{callback.from_user.id}".join(random.sample(letters_and_digits, 10))
    rand_string = "".join(random.sample(letters_and_digits, 10))
    if not isInit:
      try:
        amount = await state.get_data("total_amount")
        amount = amount["total_amount"]
        amount = int(amount)
      except:
        await bot.send_message(chat_id=callback.from_user.id, text="Произошла ошибка!")
        await ClientStatesGroup.Start.set()

    quickpay = Quickpay(
      receiver='4100118185732942',
      quickpay_form='shop',
      targets='@At1sets_TimeManager_bot',
      paymentType='SB',
      sum=amount,
      label=rand_string
    )

    chat_id = callback.from_user.id
    await db.add_user(user_id=callback.from_user.id, name=callback.from_user.full_name)
    await db.update_label(user_id=chat_id, label=rand_string)
    if callback.data == "back_to_payment":
      await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
    return await bot.send_message(chat_id=chat_id, text="Готово, теперь вы можете оплатить по ссылке ниже! После оплаты, нажмите на кнопку \"Завершить олату\"", reply_markup=setInlineKeyboard(
      InlineKeyboardButtons=[InlineKeyboardButton(text="Открыть форму", url=quickpay.redirected_url),
                             InlineKeyboardButton(text="Завершить олату", callback_data="claim")],
    mode=2))
  

  elif callback.data == "claim":
    try:
      data = await db.get_payment_status(user_id=callback.from_user.id)
      isPayd = data[-1][0]
      label = data[-1][1]
      chat_id = callback.from_user.id
      client = Client(API_YOOMONEY_PAYMENT)
      history = client.operation_history(label=label)
      operations = history.operations
      if len(operations) > 0:
        operation = operations[-1]
        amount_sum = operation.amount
        try:
          if operation.status == "success":
            await bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text="Оплата прошла успешно!")
            await db.update_label(user_id=chat_id, label='1')
            await db.update_payment_status(user_id=chat_id)
            await db.update_payment_count(user_id=chat_id)
            await db.update_total_amount(user_id=chat_id, amount=amount_sum)
            message = "Спасибо за поддержку! Благодаря вам я буду дальше развиваться, чтобы мною было еще комфортнее пользоваться!"
            if isPayd:
              message = "Ого, вы решили меня еще поддержать! Большое вам спасибо 😉 Я непременно вас запомню и, в дальнейшем выдам некоторые плюшки 🙈, только тссс!"
            await bot.send_message(chat_id=chat_id, text=message)
            await asyncio.sleep(1)
            sticker="CAACAgIAAxkBAAEIvzdkSjBDufLgkvRK8sdtE7OmgrAv5QACchIAAkblqUjyTBtFPtcDUS8E"
            if isPayd:
              sticker = "CAACAgIAAxkBAAEIxz1kTTNPBgXBkkJmnsuxiBj79wzrjQAC2R8AAv2MKEpe539ds6rQhS8E"
            await bot.send_sticker(chat_id=chat_id, sticker=sticker)
            await state.reset_data()
            return await ClientStatesGroup.Start.set()
          else:
            return await bot.send_message(chat_id=chat_id, text="Вы еще не произвели платеж! Или же статус платежа еще обрабатывается.")
        except:
          return await bot.send_message(chat_id=chat_id, text="Произошла ошибка! Извините за предоставленные неудобства :(")
      elif isPayd:
        await bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text="Завершить оплату -> вы уже являетесь Premium")
        await bot.send_message(chat_id=chat_id, text="Еще раз cпасибо за поддержку! Мне действительно приятно :)")
        await asyncio.sleep(1)
        await bot.send_message(chat_id=chat_id, text="При желании, вы всегда можете поддержать меня неограниченное колличество раз.")
        await asyncio.sleep(1)
        await bot.send_sticker(chat_id=chat_id, sticker="CAACAgIAAxkBAAEIxyxkTSnLjHcab7Wu08tDHOHsMmVujAACiSIAAsSb6Us7ZFai5iiSfC8E")
        await state.reset_data()
        return await ClientStatesGroup.Start.set()
      else:
        await callback.answer(text="Вы еще не отправляли платеж!", show_alert=True)
        return await bot.edit_message_text(chat_id=chat_id, message_id=callback.message.message_id, text="Вернуться к оплате?",
                                           reply_markup=setInlineKeyboard(InlineKeyboardButtons=[
                                             InlineKeyboardButton(text="Вернуться", callback_data="back_to_payment"),
                                             InlineKeyboardButton(text="Выйти", callback_data="quit")
                                           ], mode=2))
    except:
      await bot.send_message(chat_id=callback.from_user.id, text="Произошла ошибка!")

  elif callback.data == "QIWI":
    pass

async def send_alerts(message):
  users = os.listdir("./data/users")
  for user in users:
    try:
      await bot.send_message(user, text=message, reply_markup=removeKeyboard())
    except:
      continue

async def on_startup(_):
  await bot.send_message(ADMIN_ID, text="bot starting!", reply_markup=removeKeyboard())
  global isDevelopment
  if not isDevelopment:
    message = "Меня починили!"
    return await send_alerts(message=message)
  else:
    with open("./data/blacklist.txt", "w") as file:
      return file.close()

async def on_shutdown(_):
  await bot.send_message(ADMIN_ID, text="bot down!", reply_markup=removeKeyboard())
  global isDevelopment
  if not isDevelopment:
    message = "Бот отключен. Вероятнее всего, он находится на технической паузе, приймите извинения за неудобства!"
    # Останавливаем все занятия
    users = os.listdir("./data/users")
    for user in users:
      await main_functions.stopRecording(user_id=user)
    return await send_alerts(message=message)
  else:
    await main_functions.stopRecording(user_id=ADMIN_ID)

if __name__ == "__main__":
  executor.start_polling(dispatcher=dispatcher, skip_updates=False, on_startup=on_startup, on_shutdown=on_shutdown)