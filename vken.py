import discord
from discord.ext import commands
import os
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import cogs.dbmanage as dbmanage

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

# 年、月が替わったらリセットをかける
scheduler = BackgroundScheduler()
scheduler.add_job(dbmanage.monthly_initialize, CronTrigger(day=1, hour=0, minute=0, second=0))
scheduler.add_job(dbmanage.anual_initialize,CronTrigger(month=1, day=1, hour=0, minute=0, second=0))
scheduler.start()

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