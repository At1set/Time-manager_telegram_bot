import time_manager as main_functions
from visualizer import create_statistick
from config import *
from Api_token import *

import os
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

storage = MemoryStorage()

# PROXY_URL = "http://proxy.server:3128"
# bot = Bot(API_TOKEN, proxy=PROXY_URL)

bot = Bot(API_TOKEN)
dispatcher = Dispatcher(bot, storage=storage)

class ClientStatesGroup(StatesGroup):
  Start = State()
  Wait = State()
  Recording_time = State()
  Recording_time_editmessage = State()
  Recording_employment = State()
  Getting_new_employment = State()
  Setting_new_employment = State()
  Deleteing_employment = State()

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

# INLINE KEYBOARDЖ
def setInlineKeyboard(InlineKeyboardButtons, mode=1) -> InlineKeyboardMarkup:
  keyboard = InlineKeyboardMarkup()
  if mode == 1:
    keyboard.add(InlineKeyboardButtons)
  else:
    for inlineButton in InlineKeyboardButtons:
      keyboard.add(inlineButton)
  return keyboard
# =================================================================================



# =============================ОБРАБОТЧИКИ КОМАНД БОТА=============================
@dispatcher.message_handler(lambda message: message.text != "/start", state=[None])
async def hello(message: types.Message):
  await message.answer('Для того, чтобы начать, введи:\n/start')


@dispatcher.message_handler(state=[ClientStatesGroup.Wait, ClientStatesGroup.Setting_new_employment, ClientStatesGroup.Recording_employment, ClientStatesGroup.Deleteing_employment])
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

@dispatcher.message_handler(commands=["help", "menu", "about", "info", "info_1", "info_2", "info_3", "info_4", "info_5", "info_6", "start_task_recording"], state="*")
async def commands(message: types.Message, state: FSMContext):
  if message.text == "/start_task_recording":
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
    await ClientStatesGroup.Start.set()

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
      curr_day = int(message.text.replace("/info_", "").strip())
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
        if result_message != "":
          await asyncio.sleep(0.5)
          await message.answer(text=f"Также вам доступна статистика за другие дни:\n{more_info_message}")
      elif count_days-1 == curr_day:
        await message.answer(text=f"Ваша статистика за вчера:\n{result_message}")
        if result_message != "":
          await asyncio.sleep(0.5)
          await message.answer(text=f"Также вам доступна статистика за другие дни:\n{more_info_message}")
      elif count_days-2 == curr_day:
        await message.answer(text=f"Ваша статистика за позавчера:\n{result_message}")
        if result_message != "":
          await asyncio.sleep(0.5)
          await message.answer(text=f"Также вам доступна статистика за другие дни:\n{more_info_message}")
      else:
        await message.answer(text=f"Ваша статистика за {curr_day} день записи:\n{result_message}")
        if result_message != "":
          await asyncio.sleep(0.5)
          await message.answer(text=f"Также вам доступна статистика за другие дни:\n{more_info_message}")

  elif (message.text == "/start_task_recording"):
    if curr_state != "ClientStatesGroup:Recording_time" and curr_state != "ClientStatesGroup:Recording_time_editmessage":
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

@dispatcher.message_handler(lambda message: not "/" in message.text, state=[ClientStatesGroup.Recording_time, ClientStatesGroup.Recording_time_editmessage])
async def choice_employment(message: types.Message, state: FSMContext):
  curr_state = await state.get_state()
  isMessageEdit = curr_state == "ClientStatesGroup:Recording_time_editmessage"
  await ClientStatesGroup.Recording_employment.set()
  employment = message.text
  _message = await message.answer(text=f'Начата запись: \n{employment}', reply_markup=setInlineKeyboard([InlineKeyboardButton(text='Изменить', callback_data=message.message_id),
                                                                                              InlineKeyboardButton(text='Закончить', callback_data="break")],
                                                                                              mode=2))
  await main_functions.startRecording(user_id=message.from_user.id, employment=employment, isMessageEdit=isMessageEdit)
  data = {"buffer_inline_message": _message}
  await state.set_data(data)

@dispatcher.message_handler(commands=["set_new_employment"], state=[ClientStatesGroup.Recording_time, ClientStatesGroup.Recording_time_editmessage])
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
@dispatcher.message_handler(commands=["exit"], state=[ClientStatesGroup.Recording_time, ClientStatesGroup.Recording_time_editmessage, ClientStatesGroup.Start])
async def exit_from_state(message: types.Message, state: FSMContext):
  await message.delete()
  await bot.send_message(message.from_user.id, text='Вы вышли из режима записи. Не волнуйтесь, все ваши действия сохранятся.', reply_markup=removeKeyboard())

  return await state.finish()
# =================================================================================

@dispatcher.callback_query_handler(lambda callback: callback.data == "start_continue", state="*")
async def callback_onStart(callback: types.CallbackQuery):
  await bot.send_message(callback.from_user.id, text=MESSAGE__MAIN_MENU, parse_mode="HTML")
  await bot.answer_callback_query(callback.id)


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
    employment = callback["message"]["text"][16:]
    time_interval = await main_functions.stopRecording(user_id=chat_id, employment=employment)
    if time_interval:
      time_difference = await main_functions.calc_time(time_interval)
      await bot.send_message(chat_id=chat_id, text=f"Дело завершено!\nВремя, затраченное на него у вас составило: {time_difference}")
    else:
      await bot.send_message(chat_id=chat_id, text="Странно хмм..., но, видимо, данное действие было уже завершено. Непридвиденная ошибка.")
    await asyncio.sleep(2)
    await bot.send_message(chat_id=chat_id, text="Ожидание ввода...")
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

async def send_alerts(message):
  users = os.listdir("./data/users")
  for user in users:
    try:
      await bot.send_message(user, text=message, reply_markup=removeKeyboard())
    except:
      continue

async def on_startup(_):
  message = "Меня починили!"
  return await send_alerts(message=message)

async def on_shutdown(_):
  message = "Бот находится на технической паузе, приймите извинения за неудобства!"
  return await send_alerts(message=message)


if __name__ == "__main__":
  executor.start_polling(dispatcher=dispatcher, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)