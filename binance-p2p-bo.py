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
        return [
            f"{offer['price']:>7} BOB - {offer['name']:<20} ( min: {offer['min']:>7}  max: {offer['max']:>7} )"
            for offer in offers
        ]

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

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

frame = tk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew")
frame.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)

listbox = tk.Listbox(frame, font=("Courier New", 14), width=70, height=15)
listbox.grid(row=0, column=0, sticky="nsew")

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

listbox.config(yscrollcommand=scrollbar.set)

update_prices()
root.mainloop()
