import discord
from discord.ext import commands, tasks
import datetime
import os
from flask import Flask
from threading import Thread

# -------- Serwer keep_alive --------
app = Flask('')

@app.route('/')
def home():
    return "Bot działa!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ------------------------------------

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True  # to pozwala czytać wiadomości

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    send_daily_message.start()  # uruchamia zadanie co 60 sek

@bot.command()
async def test(ctx):
    await ctx.send("Działam normalnie 🎯")

@tasks.loop(minutes=1)
async def send_daily_message():
    now = datetime.datetime.now() + datetime.timedelta(hours=2)  # zmiana strefy czasowej
    print(f"Aktualna godzina na Repl.it: {now}")

    if now.hour == 23 and now.minute == 17:
        try:
            with open('wiadomosci.txt', 'r', encoding="utf-8") as f:
                lines = f.readlines()
                day = now.strftime('%A')  # Monday, Tuesday...

                line = next((l for l in lines if l.split(' ')[0].strip().lower() == day.lower()), None)

                if line:
                    msg = line.split(' ', 1)[1].strip()
                else:
                    msg = "Brak wiadomości na dziś."

                channel = bot.get_channel(CHANNEL_ID)
                await channel.send(msg)

        except Exception as e:
            print(f"Błąd: {e}")

# -------- Start ----------
keep_alive()
bot.run(TOKEN)
