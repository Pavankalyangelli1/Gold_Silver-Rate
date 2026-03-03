from flask import Flask, render_template, jsonify
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

def fetch_prices():
    usd_inr = yf.Ticker("USDINR=X").history(period="1d")["Close"].iloc[-1]

    gold_usd = yf.Ticker("GC=F").history(period="1d")["Close"].iloc[-1]
    silver_usd = yf.Ticker("SI=F").history(period="1d")["Close"].iloc[-1]

    gold_inr = gold_usd * usd_inr
    silver_inr = silver_usd * usd_inr

    gold_22k = (gold_inr / 31.1035) * 10 * 0.916
    silver_kg = (silver_inr / 31.1035) * 1000

    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "gold": round(gold_22k, 2),
        "silver": round(silver_kg, 2)
    }

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api")
def api():
    return jsonify(fetch_prices())

if __name__ == "__main__":
    app.run(debug=True)