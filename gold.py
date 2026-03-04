import yfinance as yf
import pandas as pd
import time
import requests
from datetime import datetime
import matplotlib.pyplot as plt

# ========== SETTINGS ==========
TELEGRAM_TOKEN = "AAHPKZDUdaVqmqqpvwpP64tKKXzd4cLAVkU"
CHAT_ID = " "
PRICE_DROP_ALERT = 500   # Alert if gold drops ₹500 from last saved value
FILE_NAME = "live_rates.xlsx"
# ==============================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

def fetch_prices():
    gold_usd = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
    silver_usd = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]
    usd_inr = yf.Ticker("USDINR=X").history(period="1d")["Close"].iloc[-1]
    gold_inr_per_ounce  = gold_usd * usd_inr
    silver_inr_per_ounce  = silver_usd * usd_inr
    
    gold_per_gram = gold_inr_per_ounce  / 31.1035
    gold_24k_10g = gold_per_gram * 10
    gold_22k_10g = gold_24k_10g * 0.916   # 22K purity

    # Silver (already INR)
    silver_per_gram = silver_inr_per_ounce / 31.1035
    silver_per_kg = silver_per_gram * 1000

    # Vijayawada jewellery estimation (approx)
    making_charge = 12  # %
    silver_making = 8  # %
    gst = 3  # %

    Vijayawada_22k = gold_22k_10g * (1 + making_charge/100)
    Vijayawada_22k *= (1 + gst/100)

    # Silver jewellery estimation (₹ per kg)
    Vijayawada_silver = silver_per_kg * (1 + silver_making/100)
    Vijayawada_silver *= (1 + gst/100)

    return gold_24k_10g, gold_22k_10g, silver_per_kg, Vijayawada_22k, Vijayawada_silver


def save_to_excel(data):
    df = pd.DataFrame([data])
    try:
        old = pd.read_excel(FILE_NAME)
        df = pd.concat([old, df], ignore_index=True)
    except:
        pass
    df.to_excel(FILE_NAME, index=False)


def plot_graph():
    df = pd.read_excel(FILE_NAME)
    plt.figure()
    plt.plot(df["Gold_22K"], label="Gold 22K (₹/10g)")
    plt.plot(df["Silver"], label="Silver (₹/kg)")
    plt.legend()
    plt.xlabel("Data Points")
    plt.ylabel("Price")
    plt.title("Live Gold & Silver Prices")
    plt.show()


print("Running Live Monitoring...\n")

last_gold_price = None

while True:
    try:
        gold24, gold22, silver, vijayawada, chennai_silver = fetch_prices()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{now}")
        print(f"Gold 24K: ₹{gold24:.2f} /10g")
        print(f"Gold 22K: ₹{gold22:.2f} /10g")
        print(f"Silver: ₹{silver:.2f} /kg")
        print(f"Vijayawada Est 22K Jewellery: ₹{vijayawada:.2f} /10g")
        print(f"Vijayawada Silver Jewellery Est: ₹{chennai_silver:.2f} /kg")

        data = {
            "Time": now,
            "Gold_24K": round(gold24,2),
            "Gold_22K": round(gold22,2),
            "Silver": round(silver,2),
            "Chennai_22K_Est": round(vijayawada,2),
            "Chennai_Silver_Est": round(chennai_silver,2)
        }

        save_to_excel(data)

        # Telegram alert
        if last_gold_price and (last_gold_price - gold22) >= PRICE_DROP_ALERT:
            send_telegram(f"⚠ Gold dropped ₹{PRICE_DROP_ALERT}! Now ₹{gold22:.2f}")
        last_gold_price = gold22

        time.sleep(10)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
