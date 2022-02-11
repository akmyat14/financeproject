import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import tkinter as tk
from tkinter import ttk
import matplotlib
from datetime import datetime

matplotlib.use("TkAgg")

url = 'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2021-01-01/2022-01-01?adjusted=false&sort=asc&limit=5000'

#headers = {'Authorization': 'Bearer'}

response = requests.get(url, headers=headers).json()

print(response["resultsCount"])
root = tk.Tk()
root.title('Some graph')
root.geometry('1000x1000')


def quit(root):
    root.destroy()


fig = plt.figure(figsize=(5, 5), dpi=100)
fig.suptitle("Figure title")

plot = fig.add_subplot(1, 1, 1)
plot.set_title("Apple Stock")

x_values = []
prices = []

for x in range(0, 252):
    unix_time = (response['results'][x]['t'])/1000.0
    date_time = datetime.fromtimestamp(unix_time).strftime('%d/%m/%Y')
    x_values.append(date_time)
    prices.append(response['results'][x]['vw'])

print(datetime.fromtimestamp(
    (response['results'][x]['t'])/1000.0).strftime('%d/%m/%Y'))

plot.plot(x_values, prices, color='blue')
plot.set_xticks(x_values[::7])
plot.set_xticklabels(x_values[::7], rotation=45)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0)

tk.Button(root, text="Quit", command=lambda root=root: quit(
    root)).grid(row=1, column=0)

root.mainloop()
