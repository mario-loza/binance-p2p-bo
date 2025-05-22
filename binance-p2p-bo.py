import datetime
import requests
import tkinter as tk

CURRENCY = 'BOB'
ASSET = 'USDT'
TRADE_TYPE = 'SELL'

def fetch_p2p_data():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "asset": ASSET,
        "fiat": CURRENCY,
        "merchantCheck": True,
        "page": 1,
        "rows": 20,
        "payTypes": [],
        "tradeType": TRADE_TYPE,
        "publisherType":"merchant"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        ads = data['data']
        offers = [{
            "price": float(ad['adv']['price']),
            "name": ad['advertiser']['nickName']
        } for ad in ads]
        offers.sort(key=lambda x: x['price'], reverse=True)
        return [f"{offer['price']} {CURRENCY} - {offer['name']}" for offer in offers]

    except Exception as e:
        return [f"Error: {e}"]

def update_prices():
    prices = fetch_p2p_data()
    listbox.delete(0, tk.END)
    for p in prices:
        listbox.insert(tk.END, p)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    root.title(f"Mejores Precios P2P - USDT to BOB (Binance - {now})")
    root.after(15000, update_prices)

root = tk.Tk()
root.title("Mejores Precios P2P - USDT to BOB (Binance)")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

listbox = tk.Listbox(frame, font=("Helvetica", 14), width=50, height=15)
listbox.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

update_prices()
root.mainloop()
