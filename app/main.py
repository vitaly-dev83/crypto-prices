from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

DEFAULT_COINS = ["bitcoin", "ethereum", "dogecoin"]
DEFAULT_CURRENCY = "usd"

def fetch_crypto_prices(coins, vs_currency="usd"):
    """Запрашивает текущие курсы криптовалют с CoinGecko API."""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coins),
        "vs_currencies": vs_currency,
        "include_last_updated_at": "true",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def process_data(raw_data, coins, vs_currency):
    """Преобразует сырые данные в список словарей."""
    if not raw_data:
        return []

    result = []
    for coin in coins:
        coin_data = raw_data.get(coin, {})
        price = coin_data.get(vs_currency, "N/A")
        last_updated = coin_data.get("last_updated_at", None)

        if last_updated:
            last_updated = datetime.fromtimestamp(last_updated).strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_updated = "Unknown"

        result.append({
            "coin": coin.capitalize(),
            "symbol": coin[:3].upper(),
            "price": price,
            "last_updated": last_updated,
        })
    return result

@app.route("/")
def index():
    raw_data = fetch_crypto_prices(DEFAULT_COINS, DEFAULT_CURRENCY)
    prices = process_data(raw_data, DEFAULT_COINS, DEFAULT_CURRENCY)
    last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", prices=prices, last_refresh=last_refresh)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)