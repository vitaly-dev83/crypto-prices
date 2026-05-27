#!/usr/bin/env python3
"""
Crypto Currency Price Fetcher

Получает текущие курсы криптовалют с CoinGecko API.
Поддерживает аргументы командной строки для гибкости.
"""

import requests
import json
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Optional

DEFAULT_COINS = ["bitcoin", "ethereum", "dogecoin"]
DEFAULT_CURRENCY = "usd"


def fetch_crypto_prices(
    coins: List[str], vs_currency: str = "usd"
) -> Optional[Dict]:
    """Запрашивает текущие курсы криптовалют с CoinGecko API"""
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
    except requests.exceptions.RequestException as e:
        print(f"❌ API request error: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print("❌ Invalid JSON response from API", file=sys.stderr)
        return None


def process_data(
    raw_data: Dict, coins: List[str], vs_currency: str
) -> List[Dict]:
    """Преобразует сырые данные в структурированный список"""
    if not raw_data:
        return []

    result = []
    for coin in coins:
        coin_data = raw_data.get(coin, {})
        price = coin_data.get(vs_currency, "N/A")
        last_updated = coin_data.get("last_updated_at", "Unknown")

        if last_updated != "Unknown":
            last_updated = datetime.fromtimestamp(last_updated).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        result.append(
            {
                "coin": coin.capitalize(),
                "price_usd": price,
                "last_updated": last_updated,
            }
        )
    return result


def save_to_json(data: List[Dict], filename: str = "crypto_prices.json") -> None:
    """Сохраняет результат в JSON-файл"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved to {filename}")


def print_to_console(data: List[Dict]) -> None:
    """Выводит результат в консоль в читаемом виде"""
    print("\n" + "=" * 50)
    print("📊 CRYPTO CURRENCY PRICES")
    print("=" * 50)
    for item in data:
        print(f"  • {item['coin']}: ${item['price_usd']}")
        print(f"    Updated: {item['last_updated']}")
        print()
    print("=" * 50)


def parse_args():
    """Парсит аргументы командной строки"""
    parser = argparse.ArgumentParser(
        description="Fetch current cryptocurrency prices from CoinGecko API"
    )
    parser.add_argument(
        "--coins",
        nargs="+",
        default=DEFAULT_COINS,
        help=f"Coins to fetch (default: {', '.join(DEFAULT_COINS)})",
    )
    parser.add_argument(
        "--currency",
        default=DEFAULT_CURRENCY,
        help=f"Target currency (default: {DEFAULT_CURRENCY})",
    )
    parser.add_argument(
        "--output",
        default="crypto_prices.json",
        help="Output JSON filename (default: crypto_prices.json)",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress console output"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching prices...")

    raw_data = fetch_crypto_prices(args.coins, args.currency)

    if raw_data:
        processed_data = process_data(raw_data, args.coins, args.currency)
        save_to_json(processed_data, args.output)

        if not args.quiet:
            print_to_console(processed_data)
    else:
        print("❌ Failed to fetch data from API", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()