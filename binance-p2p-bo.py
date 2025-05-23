#crea el exe asi: pyinstaller --onefile --noconsole binance-p2p-bo.py --icon=profit.ico --add-data "profit.ico;." 

import datetime
import requests
import tkinter as tk
from winotify import Notification
import os
import sys
import winshell
from win32com.client import Dispatch

APP_NAME = "Binance P2P-BO"

CURRENCY = 'BOB'
ASSET = 'USDT'
TRADE_TYPE = 'SELL'

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def create_shortcut_if_needed():
    shortcut_path = os.path.join(winshell.start_menu(), f"{APP_NAME}.lnk")
    if os.path.exists(shortcut_path):
        return

    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = exe_path
    shortcut.WorkingDirectory = os.path.dirname(exe_path)
    shortcut.IconLocation = exe_path
    shortcut.save()

def show_notification(title, message):
    icon_path = resource_path("profit.ico")
    toast = Notification(
        app_id=APP_NAME,
        title=title,
        msg=message,
        duration="short",
        icon=icon_path)
    toast.show()

def fetch_p2p_data():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "fiat": CURRENCY,
        "page": 1,
        "rows": 20,
        "tradeType": TRADE_TYPE,
        "asset": ASSET,
        "countries": [],
        "proMerchantAds": False,
        "shieldMerchantAds": False,
        "filterType": "all",
        "periods": [],
        "additionalKycVerifyFilter": 0,
        "publisherType":"merchant",
        "payTypes": [],
        "classifies": ["mass","profession", "fiat_trade"],
        "tradedWith": False,
        "followed": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        ads = data['data']
        offers = [{
            "price": float(ad['adv']['price']),
            "name": ad['advertiser']['nickName'],
            "min": ad['adv']['minSingleTransAmount'],
            "max": ad['adv']['maxSingleTransAmount']
        } for ad in ads]
        offers.sort(key=lambda x: x['price'], reverse=True)
        return offers

    except Exception as e:
        return [f"Error: {e}"]

def update_prices():

    offers = fetch_p2p_data()
    listbox.delete(0, tk.END)

    for offer in offers:
        if "error" in offer:
            listbox.insert(tk.END, f"Error: {offer['error']}")
            continue
        line = f"{offer['price']:>7} BOB - {offer['name']:<20} ( min: {offer['min']:>7}  max: {offer['max']:>7} )"
        listbox.insert(tk.END, line)

    if notify_var.get():
        try:
            threshold = float(entry.get())
            top_price = offers[0]['price']
            if top_price >= threshold:
                show_notification( "¡Precio USDT alcanzado!",f"Precio actual: {top_price:.2f} BOB" )
        except ValueError:
            pass  

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    root.title(f"Mejores Precios P2P - USDT to BOB (Binance - {now})")
    root.after(15000, update_prices)

create_shortcut_if_needed()

root = tk.Tk()
icon_path = resource_path("profit.ico")
root.iconbitmap(icon_path)

root.title("Mejores Precios P2P - USDT to BOB (Binance)")

root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

tk.Label(top_frame, text="Avisarme si el precio ≥ ").pack(side=tk.LEFT)
entry = tk.Entry(top_frame, width=10)
entry.pack(side=tk.LEFT, padx=(5, 5))
tk.Label(top_frame, text="BOB").pack(side=tk.LEFT)

notify_var = tk.BooleanVar(value=False)
notify_checkbox = tk.Checkbutton(top_frame, text="Activar notificación", variable=notify_var)
notify_checkbox.pack(side=tk.LEFT, padx=(10, 0))

frame = tk.Frame(root)
frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
frame.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)

listbox = tk.Listbox(frame, font=("Courier New", 14), width=70, height=15)
listbox.grid(row=0, column=0, sticky="nsew")

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
listbox.config(yscrollcommand=scrollbar.set)

root.update_idletasks()
root.geometry(f"{root.winfo_width()}x{root.winfo_height()}")

listbox.config(yscrollcommand=scrollbar.set)

update_prices()
root.mainloop()
