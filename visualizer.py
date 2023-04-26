import asyncio
import json
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from datetime import datetime

from time_manager import calc_time

# rcParams['font.sans-serif'] = ['Arial Unicode MS']

def luminance(hex_color):
  hex = hex_color.strip("#")
  r, g, b = [int(hex[i:i+2], 16) for i in (0, 2, 4)]
  luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255 * 100
  return luminance

async def create_statistick(user_id, paint_over_between=False):
  # Получаем ластовый datajson file
  current_jsonfile = "data.json"
  number_of_jsonfile = len(os.listdir(f"./data/users/{user_id}/"))-3
  if number_of_jsonfile > 1:
    current_jsonfile = f"data_{number_of_jsonfile-1}.json"
  if not os.path.exists(f'./data/users/{user_id}/{current_jsonfile}'):
    return False
  else:
    with open(f'./data/users/{user_id}/{current_jsonfile}', 'r', encoding="utf-8-sig") as file:
      data = json.load(file)
      if len(data) == 0:
        return False
  
  fig = plt.figure(figsize=(19, 10))
  fig.subplots_adjust(top=0.9,bottom=0.1,left=0.09,right=0.99,hspace=0.2,wspace=0.2)

  yMax = 7.2
  yMin = 0

  xMin = 0
  xMax = 24

  plt.ylim(yMax, yMin)
  plt.xlim(xMin, xMax)

  weekDays = ['ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
  yTicks, yLabels = [], []
  for i in range(1, 8):
    yTicks.append(i-0.8)
    yTicks.append(i-0.4)
    yTicks.append(i)

    yLabels.append('')
    yLabels.append(weekDays[i-1])
    yLabels.append('')

  plt.yticks(yTicks, yLabels, fontweight='bold', fontstyle='italic', family='serif')

  xTicks, xLabels = [], []
  for i in range(xMin, xMax):
    xTicks.append(int(i))
    for delimiter in range(1,5):
      xTicks.append(i+delimiter/4)

  for i in xTicks:
    if int(i) == i:
      xLabels.append(int(i))
      continue
    xLabels.append('')

  plt.xticks(xTicks, xLabels)

  plt.ylabel('Дни')
  plt.xlabel('Время')
  plt.grid(zorder=0, axis="both")

  colors = ["#fd33d2", "#c8c49e", "#ec1300", "#2cc960", "#9fc926", "#5997e6", "#a8c2bc", "#f58642", "#72f499", "#4b113b", "#e6878a", "#c6e65d", "#c6e65d", "#3bf2e6", "#021b05", "#cf240f", "#dcf49d", "#b72fb2"]
  
  barh_left = 0
  with open(f'./data/users/{user_id}/{current_jsonfile}', 'r', encoding="utf-8-sig") as file:
    data = json.load(file)
    curr_week_day = data["1"][list(data["1"].keys())[0]][0]
    date_object = datetime.strptime(curr_week_day, "%S-%M-%H-%d-%m-%Y")
    curr_week_day = date_object.weekday()

    # Сбор уникальных занятий
    uniq_employments = set()
    for i in range(1, len(data)+1):
      curr_day = data[str(i)]
      for employment in curr_day:
        if not "_" in employment:
          uniq_employments.add(employment)

    legend_labels = set()
    if paint_over_between:
      space_label_limit = True
    for i in range(curr_week_day+1, curr_week_day+len(data)+1):
      if i > 7:
        break
      curr_day = data[str(i-curr_week_day)] # 1, 2, 3, 4...

      for employment in curr_day:
        time_interval = curr_day[employment]

        space_left = barh_left
        limit_different = xMax - barh_left

        # Получаем barh_left
        stopTime_day = int(time_interval[1].split("-")[3])
        startTime = time_interval[0].split("-")
        startTime_sec, startTime_min, startTime_hours, startTime_day, startTime_month, startTime_year      = [int(i) for i in startTime]
        total_start_sec   = startTime_hours * 3600 + startTime_min * 60 + startTime_sec
        number_of_employment = list(curr_day.keys()).index(employment)

        barh_left = total_start_sec / 3600
        if stopTime_day != startTime_day and number_of_employment == 0:
          barh_left = 0
        # Продолжаем...

        space_right = barh_left

        time_interval = await calc_time(time_interval=time_interval, mode=2)
        difference_hours, difference_min = divmod(time_interval, 3600)
        difference_min, difference_sec = divmod(difference_min, 60)

        if difference_hours == 0 and difference_min == 0 and difference_sec == 0:
          continue

        result_hours = time_interval/3600
        if stopTime_day != startTime_day and number_of_employment == 0: # Отнимаем разницу при переходе на новый день
          result_hours -= limit_different

        barh_width = result_hours
        barh_height = 0.8
        barh_color = ""

        legend_label = ''
        for uniq_employment in uniq_employments:
          if uniq_employment in employment:
            if uniq_employment == "Сон":
              barh_color = "#0804da"
            else:
              color_inex = list(uniq_employments).index(uniq_employment) #берем индекс уникального employment для взятия цвера
              barh_color = f"{colors[color_inex]}"
            legend_label = uniq_employment
            for label in legend_labels:
              if legend_label == label:
                legend_label = None
            legend_labels.add(uniq_employment)

        label_color = "white" if luminance(barh_color) < 50 else "black"

        bar = plt.barh(i-0.4, width=barh_width, height=barh_height, left=barh_left, color=barh_color, zorder=4, label=legend_label, edgecolor="black")

        # Заполняем промежутки между занятиями
        if paint_over_between:
          legend_label = None
          if space_label_limit:
            legend_label = "Другое"
            space_label_limit = False
          space_width = space_right - space_left
          space = plt.barh(i-0.4, width=space_width, height=barh_height, left=space_left, color="black", zorder=4, label=legend_label, edgecolor="black")
          plt.bar_label(space, label_type="center", zorder=10, labels=["Другое"], color="#dac2c5", fontweight="bold")
        # Рисуем стрелочку для перехода на новый день:
        if (startTime_day != stopTime_day and number_of_employment != 0):
          if barh_left < 23.4:
            plt.bar_label(bar, label_type="center", zorder=10, labels=["➟"], color=label_color, fontweight="bold", fontsize=40)
          continue

        if difference_hours == 0 and difference_min == 0:
          continue
        elif difference_hours == 0:
          if difference_min > 8:
            plt.bar_label(bar, label_type="center", zorder=10, labels=[f"{difference_min}м,{difference_sec}с"], color=label_color, rotation=90, fontweight="bold")
          else:
            continue
        else:
          if difference_min > 0:
            plt.bar_label(bar, label_type="center", zorder=10, labels=[f"{difference_hours}ч,{difference_min}м"], color=label_color, fontweight="bold")
          else:
            plt.bar_label(bar, label_type="center", zorder=10, labels=[f"{difference_hours}ч"], color=label_color, fontweight="bold")
  
  if len(legend_labels) < 5:
    plt.legend(loc="upper center", bbox_to_anchor=(0.45, 1.13), ncol=10, framealpha = 0.1, shadow = True, borderpad = 1.1, fancybox = True)
  else:
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=10, framealpha = 0.1, shadow = True, borderpad = 1.1, fancybox = True)

  plt.plot()
  plt.savefig(f"./data/users/{user_id}/Temp/statistic.jpg", dpi=340)
  return True

# Для разработки
if __name__ == "__main__":
  asyncio.run(create_statistick(1925481166))