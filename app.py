from flask import Flask, render_template, jsonify
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

# ===== SETTINGS =====
MAKING_CHARGE_GOLD = 12   # %
MAKING_CHARGE_SILVER = 8  # %
GST = 3                   # %

def fetch_prices():
    # Fetch live prices
    gold_usd = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
    silver_usd = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]
    usd_inr = yf.Ticker("USDINR=X").history(period="1d")["Close"].iloc[-1]

    # Convert to INR per ounce
    gold_inr_per_ounce = gold_usd * usd_inr
    silver_inr_per_ounce = silver_usd * usd_inr

    # Convert to grams
    gold_per_gram = gold_inr_per_ounce / 31.1035
    silver_per_gram = silver_inr_per_ounce / 31.1035

    # Gold prices
    gold_24k_10g = gold_per_gram * 10
    gold_22k_10g = gold_24k_10g * 0.916

    # Silver price per kg
    silver_per_kg = silver_per_gram * 1000

    # Vijayawada Jewellery Estimation
    Vijayawada_22k = gold_22k_10g * (1 + MAKING_CHARGE_GOLD/100)
    Vijayawada_22k *= (1 + GST/100)

    Vijayawada_silver = silver_per_kg * (1 + MAKING_CHARGE_SILVER/100)
    Vijayawada_silver *= (1 + GST/100)

    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "gold_24k_10g": round(gold_24k_10g, 2),
        "gold_22k_10g": round(gold_22k_10g, 2),
        "silver_per_kg": round(silver_per_kg, 2),
        "vijayawada_22k_est": round(Vijayawada_22k, 2),
        "vijayawada_silver_est": round(Vijayawada_silver, 2)
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api")
def api():
    return jsonify(fetch_prices())

if __name__ == "__main__":
    app.run(debug=True)
