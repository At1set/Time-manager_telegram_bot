import asyncio
from aiogram.types import KeyboardButton, InlineKeyboardButton
import os
import json
from datetime import datetime
from pytz import timezone

async def write_data(user_id):
  if not os.path.exists(f'./data/users/{user_id}/data.json'):
    os.makedirs(f"./data/users/{user_id}/")
    with open(f'./data/users/{user_id}/data.json', 'w', encoding="utf-8") as file:
      file.write('{}')
  if not os.path.exists(f"./data/users/{user_id}/Temp"):
    os.mkdir(f"./data/users/{user_id}/Temp")
  if not os.path.exists(f"./data/users/{user_id}/properties.txt"):
    with open(f"./data/users/{user_id}/properties.txt", "w") as file:
      file.close()
    return
  else:
    return

async def get_employment_list(user_id, mode=1) -> KeyboardButton or InlineKeyboardButton:

  if mode == 1:
    with open('data/default/default_employment_list.txt', 'r', encoding="utf-8") as file:
      KeyboardButtons = []
      data = file.readlines()
      for line in data:
        KeyboardButtons.append(KeyboardButton(f'{line}'))

  if os.path.exists(f'./data/users/{user_id}/employment_list.txt'):
    if mode == 2:
      InlineKeyboardButtons = []
    with open(f'./data/users/{user_id}/employment_list.txt', 'r', encoding="utf-8") as file:
      data = file.readlines()
      if len(data) == 0 and mode != 1:
        return False
      for line in data:
        if line == "\n":
          continue
        if mode == 1:
          KeyboardButtons.append(KeyboardButton(f'{line.strip()}'))
        else:
          InlineKeyboardButtons.append(InlineKeyboardButton(
            text=f'{line.strip()}',
            callback_data=f'delete-{line.strip()}'
          ))
  elif mode == 2:
    return False
  if mode == 1:
    return KeyboardButtons
  else:
    return InlineKeyboardButtons

async def set_new_employment(user_id, employment):
  if not os.path.exists(f'./data/users/{user_id}/employment_list.txt'):
    f = open(f"./data/users/{user_id}/employment_list.txt", "w", encoding="utf-8")
    f.close()
  
  with open('data/default/default_employment_list.txt', 'r', encoding="utf-8") as file:
    data = file.readlines()
    for line in data:
      if employment + "\n" in data:
        return True

  with open(f"./data/users/{user_id}/employment_list.txt", "r", encoding="utf-8") as file:
    data = file.readlines()
    if employment + "\n" in data:
      return True
    with open(f"./data/users/{user_id}/employment_list.txt", "w", encoding="utf-8") as file:
      data.append(employment)
      for line in data:
        if line == "\n":
          continue
        file.write(line + "\n")
  return False

async def delete_employment_from_list(user_id, employment):
  with open(f"./data/users/{user_id}/employment_list.txt", "r", encoding="utf-8") as file:
    data = file.readlines()
    with open(f"./data/users/{user_id}/employment_list.txt", "w", encoding="utf-8") as file:
      for line in data:
        if line == "\n":
          continue
        if line == employment + "\n":
          continue
        file.write(line + "\n")
  return None

async def animate_message_loading(bot, message, text, count=2):
  _message = await bot.send_message(message.from_user.id, text)
  # получаем message_id и chat_id отправленного сообщения
  message_id = _message.message_id
  chat_id = _message.chat.id
  for a in range(1, count + 1):
    for b in range(1, 4):
      dotted = "." * b
      await bot.edit_message_text(f"{text}{dotted}", message_id=message_id, chat_id=chat_id)
      await asyncio.sleep(0.3)
    await asyncio.sleep(0.6)
  await _message.delete()
  await asyncio.sleep(0.3)



async def startRecording(user_id, employment, isMessageEdit=False):
  moscow_tz = timezone('Europe/Moscow')
  current_time = datetime.now(moscow_tz).strftime("%S-%M-%H-%d-%m-%Y") # Секунды, минуты, часы, день месяца, месяц, год
  # Получаем ластовый datajson file
  current_jsonfile = "data.json"
  number_of_jsonfile = len(os.listdir(f"./data/users/{user_id}/"))-3
  if number_of_jsonfile > 1:
    current_jsonfile = f"data_{number_of_jsonfile-1}.json"
  with open(f'./data/users/{user_id}/{current_jsonfile}', 'r', encoding="utf-8") as file:
      data = json.load(file)
      count = 0
      for days in data:
        count += 1
      try:
        with open(f'./data/users/{user_id}/{current_jsonfile}', 'w', encoding="utf-8") as file:
          _count = 1
          if not "1" in data:
            day = {}
          else:
            while True:
              if f"{_count}" in data:
                break
              else:
                _count += 1
                continue
            if count != 0:
              day = data[f"{count}"] 
            else:
              day = data[f"{count + 1}"]

          if isMessageEdit:
            # Получаем ласт employment
            last_employment = [*day][len(day)-1]
            
            matches = []
            for i in range(len(day)):
              current_key = [*day][i]
              if current_key == employment:
                matches.append(i)

            if (len(matches) == 0):
              current_time = day[last_employment]
              del day[last_employment]
              day[employment] = current_time
              if count != 0:
                data[f"{count}"] = day
              else:
                data[f"{count + 1}"] = day
              return json.dump(data, file, indent=2, ensure_ascii=False)
            elif (len(matches) == 1 and not employment + "_1" in day):
              if matches[0] == len(day)-1:
                return json.dump(data, file, indent=2, ensure_ascii=False)

          _count = 1
          if not employment in day:
            day[employment] = [current_time]
          else:
            while True:
              if not employment + f"_{_count}" in day:
                break
              else:
                _count += 1
                continue
            if isMessageEdit:
              if _count != 1 and last_employment == employment + f"_{_count-1}":
                return json.dump(data, file, indent=2, ensure_ascii=False)
              current_time = day[last_employment] 
              del day[last_employment]
              day[f"{employment}_{_count}"] = current_time
            else:
              day[f"{employment}_{_count}"] = [current_time]

          if count != 0:
            data[f"{count}"] = day
          else:
            data[f"{count + 1}"] = day
          return json.dump(data, file, indent=2, ensure_ascii=False)
      except:
        print("[ERROR IN MAIN FUNC startRecording]")
        return json.dump(data, file, indent=2, ensure_ascii=False)


async def stopRecording(user_id):
  moscow_tz = timezone('Europe/Moscow')
  current_time = datetime.now(moscow_tz).strftime("%S-%M-%H-%d-%m-%Y") # Секунды, минуты, часы, день месяца, месяц, год
  # Получаем ластовый datajson file
  current_jsonfile = "data.json"
  number_of_jsonfile = len(os.listdir(f"./data/users/{user_id}/"))-3
  if number_of_jsonfile > 1:
    current_jsonfile = f"data_{number_of_jsonfile-1}.json"
  with open(f'./data/users/{user_id}/{current_jsonfile}', 'r', encoding="utf-8") as file:
    data = json.load(file)
    count = 0
    for days in data:
      count += 1
    try:
      with open(f'./data/users/{user_id}/{current_jsonfile}', 'w', encoding="utf-8") as file:
        if count != 0:
          day = data[f"{count}"]
        else:
          day = data[f"{count + 1}"]
        
        # Получаем ластовый employment
        employment = list(day.keys())[-1]

        employment_number = ""
        if "_" in employment:
          employment, employment_number = employment.split("_")
          full_employment = employment + "_" + employment_number
        else:
          full_employment = employment

        if len(day[full_employment]) == 2:
          json.dump(data, file, indent=2, ensure_ascii=False)
          return False
        day[full_employment].append(current_time)
        time_interval = day[full_employment]
        # Перенос на новый день // неделю
        start_day, start_week_day = day[full_employment][0].split("-")[3], day[full_employment][0]
        end_day, stop_week_day = day[full_employment][1].split("-")[3], day[full_employment][1]

        date_object = datetime.strptime(start_week_day, "%S-%M-%H-%d-%m-%Y")
        start_week_day = date_object.weekday()
        date_object = datetime.strptime(stop_week_day, "%S-%M-%H-%d-%m-%Y")
        stop_week_day = date_object.weekday()

        if len(data) > 1 and stop_week_day == 0:
          print(len(data))
          if count != 0:
            data[f"{count}"] = day
          else:
            data[f"{count + 1}"] = day
          json.dump(data, file, indent=2, ensure_ascii=False)
          number_of_jsonfile = len(os.listdir(f"./data/users/{user_id}/"))-3
          with open(f'./data/users/{user_id}/data_{number_of_jsonfile}.json', 'w', encoding="utf-8") as file:
            data = {}
            data["1"] = {employment: time_interval}
            json.dump(data, file, indent=2, ensure_ascii=False)
            return time_interval

        elif start_day != end_day:
          data[count + 1] = {employment: time_interval}
          json.dump(data, file, indent=2, ensure_ascii=False)
          return time_interval
        
        else:
          if count != 0:
            data[f"{count}"] = day
          else:
            data[f"{count + 1}"] = day
          json.dump(data, file, indent=2, ensure_ascii=False)
          return time_interval

    except:
      print("[ERROR IN MAIN FUNC stopRecording]")
      json.dump(data, file, indent=2, ensure_ascii=False)
      return False

async def calc_time(time_interval, mode=1):
  if len(time_interval) == 1 or len(time_interval) == 0:
    print("[ERROR IN MAIN FUNC CALC_TIME] Переданный временной интервал либо пуст, либо в нем отсутствует начальное/конечное время!")
    return False
  startTime = time_interval[0].split("-")
  stopTime = time_interval[1].split("-")
  startTime_sec, startTime_min, startTime_hours, startTime_day, startTime_month, startTime_year   = [int(i) for i in startTime]
  stopTime_sec, stopTime_min, stopTime_hours, stopTime_day, stopTime_month, stopTime_year         = [int(i) for i in stopTime]

  total_start_sec  = startTime_hours * 3600 + startTime_min * 60 + startTime_sec
  total_stop_sec   = stopTime_hours * 3600 + stopTime_min * 60 + stopTime_sec

  if (stopTime_day != startTime_day):
    total_stop_sec += 24 * 3600

  total_difference_inSeconds = abs(total_stop_sec - total_start_sec)

  if mode == 2:
    return total_difference_inSeconds

  difference_hours, difference_min = divmod(total_difference_inSeconds, 3600)
  difference_min, difference_sec = divmod(difference_min, 60)

  if difference_hours == 0:
    time_difference = f"{difference_min} минут, {difference_sec} секунд"
  else:
    time_difference = f"{difference_hours} часов, {difference_min} минут, {difference_sec} секунд"
  
  return time_difference

async def get_day_info(user_id, day=0):
  if not os.path.exists(f'./data/users/{user_id}/data.json'):
    return [False, False]

  result_message = ""
  # Получаем ластовый datajson file
  current_jsonfile = "data.json"
  number_of_jsonfile = len(os.listdir(f"./data/users/{user_id}/"))-3
  if number_of_jsonfile > 1:
    current_jsonfile = f"data_{number_of_jsonfile-1}.json"
  with open(f'./data/users/{user_id}/{current_jsonfile}', 'r', encoding="utf-8") as file:
    data = json.load(file)
    if len(data) == 0:
      return [False, False]
    
    result_dayInfo = {}
    last_day = str(len(data))
    curr_day = data[last_day]
    if day:
      try:
        curr_day = data[str(day)]
      except:
        return [False, False]

    # Сбор уникальных занятий
    uniq_employments = []
    for employment in curr_day:
      if not "_" in employment:
        uniq_employments.append(employment)
    
    employment_sum = []
    # Сбор информации по уникальным занятиям и получаем result_dayInfo
    for uniq_employment in uniq_employments:
      employment_sum.append(uniq_employment)
      for employment in curr_day:
        for i in range(1, 10):
          if uniq_employment + f"_{i}" in employment:
            employment_sum.append(employment)
      # На данном моменте мы получаем ключи всех занятий
      employment_summTimeInSecconds = 0
      for employment in employment_sum:
        time_interval = curr_day[employment]
        total_difference_inSeconds = await calc_time(time_interval=time_interval, mode=2)
        employment_summTimeInSecconds += total_difference_inSeconds
      result_dayInfo[uniq_employment] = employment_summTimeInSecconds
      employment_sum = []

    # Работаем с result_dayInfo:
    for employment in result_dayInfo:

      total_difference_inSeconds = result_dayInfo[employment]

      difference_hours, difference_min = divmod(total_difference_inSeconds, 3600)
      difference_min, difference_sec = divmod(difference_min, 60)

      if difference_hours == 0:
        time_difference = f"{difference_min} минут, {difference_sec} секунд"
      else:
        time_difference = f"{difference_hours} часов, {difference_min} минут, {difference_sec} секунд"

      result_message += f"\nЗанятие \"{employment}\" заняло {time_difference}\n"

    return [result_message, int(last_day)]

# Для разработки
if __name__ == "__main__":
  asyncio.run(stopRecording(1925481166))