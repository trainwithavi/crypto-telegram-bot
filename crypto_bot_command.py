import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Your credentials
BOT_TOKEN = '7809107607:AAHNqVxdE8ohayfxSxlJC701AoOhSSjlQPA'
COINGECKO_API_KEY = 'CG-5CfwHjqHXuWExZzxfQBbu5bC'

def get_hot_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": 100,
        "page": 1,
        "price_change_percentage": "24h",
        "CG-5CfwHjqHXuWExZzxfQBbu5bC": COINGECKO_API_KEY
    }
    headers = {
        "CG-5CfwHjqHXuWExZzxfQBbu5bC": COINGECKO_API_KEY
    }

    response = requests.get(url, params=params, headers=headers)
    try:
        data = response.json()
    except Exception as e:
        return ["❌ Error getting data."]

    hot_coins = []
    for coin in data:
        if isinstance(coin, dict):
            change = coin.get("price_change_percentage_24h", 0)
            volume = coin.get("total_volume", 0)
            if change and change > 5 and volume > 10_000_000:
                hot_coins.append(f"{coin['name']} ({coin['symbol'].upper()}): {change:.2f}% ↑")
    return hot_coins or ["🚫 No hot coins right now."]

# 📲 Command handler
async def hotcoins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = get_hot_coins()
    message = "🚀 *Hot Coins (24h)* 🔥\n\n" + "\n".join(coins)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode="Markdown")

# 🧠 Set up app and run polling
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("hotcoins", hotcoins_command))
print("✅ Bot is running. Waiting for /hotcoins command...")
app.run_polling()
