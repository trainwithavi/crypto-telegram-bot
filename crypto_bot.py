import requests
import asyncio
from telegram import Bot

# 🔑 Replace with your real keys
BOT_TOKEN = '7809107607:AAHNqVxdE8ohayfxSxlJC701AoOhSSjlQPA'
CHAT_ID = '369086978'
COINGECKO_API_KEY = 'CG-5CfwHjqHXuWExZzxfQBbu5bC'

bot = Bot(token=BOT_TOKEN)

def get_hot_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 100,
        "page": 1,
        "price_change_percentage": "24h",
        "CG-5CfwHjqHXuWExZzxfQBbu5bC": COINGECKO_API_KEY  # ✅ Required in query
    }
    headers = {
        "CG-5CfwHjqHXuWExZzxfQBbu5bC": COINGECKO_API_KEY  # ✅ Required in header
    }

    response = requests.get(url, params=params, headers=headers)

    try:
        data = response.json()
    except Exception as e:
        print("❌ Error parsing JSON:", e)
        print("Response text:", response.text)
        return []

    hot_coins = []
    for coin in data:
        if isinstance(coin, dict):
            change = coin.get("price_change_percentage_24h", 0)
            volume = coin.get("total_volume", 0)
            if change and change > 5 and volume > 10_000_000:
                hot_coins.append(f"{coin['name']} ({coin['symbol'].upper()}): {change:.2f}% ↑")

    return hot_coins

async def send_alert():
    hot = get_hot_coins()
    if not hot:
        await bot.send_message(chat_id=CHAT_ID, text="🚫 No hot coins right now.")
    else:
        message = "🚀 *Hot Coins (24h)* 🔥\n\n" + "\n".join(hot)
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

if __name__ == "__main__":
    asyncio.run(send_alert())
