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
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Kanał do wysyłania wiadomości

# Intencje bota
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Mapowanie dni tygodnia
dni_polskie = {
    "Monday": "Poniedziałek",
    "Tuesday": "Wtorek",
    "Wednesday": "Środa",
    "Thursday": "Czwartek",
    "Friday": "Piątek",
    "Saturday": "Sobota",
    "Sunday": "Niedziela"
}

dni_angielskie = {v: k for k, v in dni_polskie.items()}

# Funkcja pomocnicza: zapisz wiadomość na konkretny dzień
def save_message_for_day(day, content):
    if os.path.exists('wiadomosci.txt'):
        with open('wiadomosci.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = []

    new_lines = []
    found = False
    for line in lines:
        if line.startswith(f"{day}:"):
            new_lines.append(f"{day}: {content}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{day}: {content}\n")

    with open('wiadomosci.txt', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

# Funkcja pomocnicza: pobierz wiadomość na dziś
def get_today_message():
    today_eng = datetime.datetime.now().strftime("%A")
    today_polish = dni_polskie.get(today_eng, today_eng)

    if os.path.exists('wiadomosci.txt'):
        with open('wiadomosci.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith(f"{today_polish}:"):
                    return line[len(today_polish)+2:].strip()
    return None

# Gdy bot się włączy
@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")
    send_daily_message.start()

# Komenda: wiadomość na dziś
@bot.command()
async def dzis(ctx):
    try:
        message = get_today_message()
        if message:
            await ctx.send(f"**CODZIENNY DYSK 👇👇**\n{message}")
        else:
            await ctx.send("Brak zaplanowanej wiadomości na dziś.")
    except Exception as e:
        await ctx.send(f"❌ Wystąpił błąd podczas pobierania wiadomości: {e}")

# Komenda: testowa
@bot.command()
async def test(ctx):
    await ctx.send("Działam normalnie 🎯")

# Zadanie: codzienna wiadomość
@tasks.loop(minutes=1)
async def send_daily_message():
    now = datetime.datetime.now() + datetime.timedelta(hours=2)
    print(f"Aktualna godzina: {now}")

    if now.hour == 12 and now.minute == 0:
        try:
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                message = get_today_message()
                if message:
                    await channel.send(f"**CODZIENNY DYSK 👇👇**\n{message}")
                else:
                    await channel.send("Brak zaplanowanej wiadomości na dziś.")
            else:
                print("Nie znaleziono kanału.")
        except Exception as e:
            print(f"Błąd przy wysyłaniu wiadomości: {e}")

# Komenda: czyść plik
@bot.command()
async def clear(ctx):
    try:
        with open('wiadomosci.txt', 'w', encoding='utf-8') as f:
            f.write('')
        await ctx.send("🧹 Plik `wiadomosci.txt` został wyczyszczony.")
    except Exception as e:
        await ctx.send(f"❌ Wystąpił błąd podczas czyszczenia pliku: {e}")

# --- KOMENDY USTAWIAJĄCE DNI (po polsku) ---

@bot.command()
async def pon(ctx, *, message):
    save_message_for_day("Poniedziałek", message)
    await ctx.send("✅ Zapisano wiadomość na **poniedziałek**!")

@bot.command()
async def wto(ctx, *, message):
    save_message_for_day("Wtorek", message)
    await ctx.send("✅ Zapisano wiadomość na **wtorek**!")

@bot.command()
async def sro(ctx, *, message):
    save_message_for_day("Środa", message)
    await ctx.send("✅ Zapisano wiadomość na **środę**!")

@bot.command()
async def czw(ctx, *, message):
    save_message_for_day("Czwartek", message)
    await ctx.send("✅ Zapisano wiadomość na **czwartek**!")

@bot.command()
async def pia(ctx, *, message):
    save_message_for_day("Piątek", message)
    await ctx.send("✅ Zapisano wiadomość na **piątek**!")

@bot.command()
async def sob(ctx, *, message):
    save_message_for_day("Sobota", message)
    await ctx.send("✅ Zapisano wiadomość na **sobotę**!")

@bot.command()
async def nie(ctx, *, message):
    save_message_for_day("Niedziela", message)
    await ctx.send("✅ Zapisano wiadomość na **niedzielę**!")

# Komenda: pokaż zawartość pliku
@bot.command()
async def poka(ctx):
    if os.path.exists('wiadomosci.txt'):
        with open('wiadomosci.txt', 'r', encoding='utf-8') as f:
            content = f.read()

        if content.strip():
            await ctx.send(f"📋 **Zawartość wiadomości:**\n```\n{content}```")
        else:
            await ctx.send("📂 Plik `wiadomosci.txt` jest pusty.")
    else:
        await ctx.send("❌ Plik `wiadomosci.txt` nie istnieje.")

# -------- Start ----------
keep_alive()
bot.run(TOKEN)
