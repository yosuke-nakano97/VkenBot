import discord
from discord.ext import commands
from discord import app_commands
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import asyncio
from dotenv import load_dotenv
from models import Expense, engine

#インテント作成
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Cogのリスト
INITIAL_EXTENSIONS = [
  'cogs.music',
  'cogs.moneytrack'
]

# .envから各種変数読み出し    
load_dotenv()

# DiscordBotを作るためのクラス
class DiscordBot(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents):
        super().__init__(
                    intents=intents,
                    command_prefix=command_prefix
                    )
    
    async def setup_hook(self):
        SERVERID = os.environ.get("SERVERID")
        self.tree.copy_global_to(guild=discord.Object(id=SERVERID))
        await self.tree.sync(guild=discord.Object(id=SERVERID))
        return await super().setup_hook()

# Botオブジェクト生成
bot = DiscordBot(intents=intents, command_prefix="!")

# Botが立ち上がったことをお知らせ
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# ボット立ち上げ
if __name__ == "__main__":
    async def boot():
        # CogをBotに登録
        for cogs in INITIAL_EXTENSIONS:
            await bot.load_extension(cogs)
    asyncio.run(boot())
    BOTTOKEN = os.environ.get("BOTTOKEN")
    
    bot.run(BOTTOKEN)