import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'✅ Бот запущен как {bot.user}')

bot.run("Your_Token")
