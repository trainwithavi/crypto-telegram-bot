import requests, random, logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ✅ Setup
BOT_TOKEN = '7809107607:AAHNqVxdE8ohayfxSxlJC701AoOhSSjlQPA'
COINGECKO_API_KEY = 'CG-5CfwHjqHXuWExZzxfQBbu5bC'
HEADERS = {"CG-5CfwHjqHXuWExZzxfQBbu5bC": COINGECKO_API_KEY}

logging.basicConfig(level=logging.INFO)

# ✅ Fetch top market data
def fetch_market_data():
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "volume_desc",
                "per_page": 100,
                "page": 1,
                "price_change_percentage": "24h"
            },
            headers=HEADERS
        )
        return res.json() if res.status_code == 200 else []
    except:
        return []

# ✅ Calculate RSI manually using hourly chart
def get_rsi_data(coin_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": 1, "interval": "hourly"}
        res = requests.get(url, params=params, headers=HEADERS).json()
        prices = [p[1] for p in res.get("prices", [])]

        if len(prices) < 15:
            return None

        gains, losses = [], []
        for i in range(1, 15):
            delta = prices[i] - prices[i - 1]
            (gains if delta > 0 else losses).append(abs(delta))

        avg_gain = sum(gains) / len(gains) if gains else 0.01
        avg_loss = sum(losses) / len(losses) if losses else 0.01
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    except:
        return None

# 🔹 TOP 5 COINS
async def top5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = fetch_market_data()
    if not coins:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 Data fetch failed.")
        return
    top = [f"{c['name']} ({c['symbol'].upper()}): {c['price_change_percentage_24h']:.2f}% ↑"
           for c in sorted(coins, key=lambda x: x.get("price_change_percentage_24h", 0), reverse=True)
           if c.get("total_volume", 0) > 10_000_000 and c.get("price_change_percentage_24h", 0) > 5][:5]
    msg = "\n".join(top) or "🚫 No hot coins."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🔥 *Top 5 Coins (24h)* 🔼\n\n{msg}", parse_mode="Markdown")

# 🔹 OVERBOUGHT
async def overbought(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = fetch_market_data()
    if not coins:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 Data fetch failed.")
        return
    selected = []
    for c in coins[:10]:  # Limit to top 25 to save time
        rsi = get_rsi_data(c["id"])
        if rsi and rsi > 70:
            selected.append(f"{c['name']} ({c['symbol'].upper()}): RSI {rsi}")
        if len(selected) >= 5:
            break
    msg = "\n".join(selected) or "🚫 No overbought coins."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📈 *Overbought Coins (RSI > 70)*\n\n{msg}", parse_mode="Markdown")

# 🔹 OVERSOLD
async def oversold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = fetch_market_data()
    if not coins:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 Data fetch failed.")
        return
    selected = []
    for c in coins[:10]:
        rsi = get_rsi_data(c["id"])
        if rsi and rsi < 30:
            selected.append(f"{c['name']} ({c['symbol'].upper()}): RSI {rsi}")
        if len(selected) >= 5:
            break
    msg = "\n".join(selected) or "🚫 No oversold coins."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"📉 *Oversold Coins (RSI < 30)*\n\n{msg}", parse_mode="Markdown")

# 🔹 WHALE DETECTOR
async def whales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = fetch_market_data()
    if not coins:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 Data fetch failed.")
        return
    whales = [f"{c['name']} ({c['symbol'].upper()}): Volume ${c['total_volume']:,}"
              for c in coins if c.get("total_volume", 0) > 300_000_000]
    msg = "\n".join(whales[:5]) or "🐋 No whale moves detected."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🐳 *Whale Volume Coins (>$300M)*\n\n{msg}", parse_mode="Markdown")

# 🔹 RANDOM COINS
async def randompick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = fetch_market_data()
    if not coins or len(coins) < 3:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🚫 Not enough data for random pick.")
        return
    rands = random.sample(coins, 3)
    picks = [f"{c['name']} ({c['symbol'].upper()}): {c.get('price_change_percentage_24h', 0):.2f}% change"
             for c in rands]
    msg = "\n".join(picks)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🎲 *Random Coin Picks*\n\n{msg}", parse_mode="Markdown")

# 🧠 Application setup
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("top5", top5))
app.add_handler(CommandHandler("overbought", overbought))
app.add_handler(CommandHandler("oversold", oversold))
app.add_handler(CommandHandler("whales", whales))
app.add_handler(CommandHandler("random", randompick))

print("✅ Bot is live — use /top5, /overbought, /oversold, /whales, /random")
app.run_polling()
