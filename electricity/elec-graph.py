import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
import numpy as np

dates = []
values = []

with open("electricity/data.csv", "r") as f:
  data = csv.reader(f)
  for row in data:
    dates.append(datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f"))
    values.append(float(row[1]))

fig, ax = plt.subplots()
ax.plot_date(dates, values, 'g')

ax.xaxis.set_major_locator(mdates.HourLocator(range(0, 25, 6)))
ax.xaxis.set_minor_locator(mdates.HourLocator(range(0, 25, 1)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

fig.autofmt_xdate()


plt.title('Room Electricity History', fontweight = "bold")
plt.show()