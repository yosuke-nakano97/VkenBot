import discord
from discord.ext import commands
import os
import asyncio
import random
import datetime
import ast
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    # MusicCogを追加
    await bot.add_cog(MusicCog(bot))
    await bot.add_cog(CoinTrackCog(bot))


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 音楽流してるとTrueにする
        self.playing = False
        self.inttraped = False
        self.flag = False

    # joinコマンド
    @commands.command()
    async def join(self, ctx):
        print("join")
        # ボットなら無視
        if ctx.author.bot:
            return
        # 送った人がボイチャにいるか
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            print(voice_channel)

            if not voice_channel:
                self.flag = False
                # ボイスチャンネルに接続していない場合は接続する
                vc = await channel.connect(timeout=30.0, self_deaf=True)
                print(f"Connected to {channel}")
            else:
                # しているとそのまま何も起こらない
                print("Already connected to a voice channel.")
        else:
            # していない場合
            print("You don't connect to a voice channel")

    # # leaveコマンド
    @commands.command()
    async def leave(self, ctx):
        print("leave")
        # ボットなら無視
        if ctx.author.bot:
            return
        # ボイチャに入ってなかったら
        if ctx.author.voice is None:
            print("you dont connect to a voice channel")
            return

        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        print(voice_channel)
        
        if voice_channel:
            
            # ボイスチャンネルにしてたら切る
            await voice_channel.disconnect()
            await self.toggle_reconnect()

            print(f"Disconnected from {voice_channel}")
        else:
            # ボイスチャンネルに入ってなかったら無視
            print("You don't connect to a voice channel.")

    # playコマンド
    @commands.command()
    async def play(self, ctx):
        print("play")
        # ボットなら無視
        if ctx.author.bot:
            return
        # ユーザーがボイチャにいなければ無視
        if ctx.author.voice is None:
            print("you dont connect to a voice channel")
            return

        voice_channel = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        # ボイチャに入っていなければ無視
        if voice_channel is None or not voice_channel.is_connected():
            return

        #   playig(２回以上してたらTrue)で１回目じゃないと無視 
        if self.playing:
            return

        try:
            await self.toggle_reconnect()
            # 1度入ると記憶
            self.playing = True
            # 音を出す所に入る
            await self.play_music(voice_channel)

        except discord.errors.ClientException as e:
            print(f"Error in play command: {e}")
        finally:
            # メソッドが終わるとFalseに
            self.playing = False
            print("fin")

    async def play_music(self, voice_channel):
        # ファイル群の名前をもらってくる
        current_directory = os.path.dirname(os.path.realpath(__file__))
        target_directory = os.path.join(current_directory, "musics")
        file_list = os.listdir(target_directory)
        # エンドレスに1つづ流す
        while voice_channel.is_connected():
            filename = random.choice(file_list)
            # ファイルのパス生成
            file_path = os.path.join(target_directory, filename)
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            print(file_path)
            # 音声流す
            voice_channel.play(discord.FFmpegPCMAudio(file_path))
            # 前の音声が流れ終わるのをまつ
            while voice_channel.is_playing():
                await asyncio.sleep(2)

                # ボイスチャンネルの状態を取得
                channel_state = discord.utils.get(bot.voice_clients, guild=voice_channel.guild)

                # もしボイスチャンネルが変更されたらループを抜ける
                if channel_state and channel_state.channel.id != voice_channel.channel.id:
                    voice_channel.stop()
                    return
            print("playend")

    async def replay(self, channel):
        #   playig(２回以上してたらTrue)で１回目じゃないと無視 
        if self.playing:
            return

        try:
            # 1度入ると記憶
            self.playing = True
            # 音を出す所に入る
            await self.play_music(channel)
        except discord.errors.ClientException as e:
            print(f"Error in play command: {e}")
        finally:
            # メソッドが終わるとFalseに
            self.playing = False 

    async def toggle_reconnect(self):
        self.flag = not self.flag
        print(f"flagchange{not self.flag} to {self.flag}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f"on_voice_state_update:member:{member},before{before},after:{after}")

        self.playing = False
        if member.name != bot.user.name:
            print("no")
            return
        
        if not before.channel:
            print("first")
            return

        if not self.flag:
            print("flag_off!")
            return

        print("yes")
        await asyncio.sleep(40)

        previous_channel = before.channel
        voice_client = discord.utils.get(bot.voice_clients, channel=previous_channel)
        i =1
        print(voice_client)
        while (voice_client is None) and i < 4:
            # ボイスチャンネルに接続していない場合は接続する
            await asyncio.sleep(40)
            voice_client = await previous_channel.connect(timeout=30.0, self_deaf=True)
            print("reConnecting")
            i+=1
        
        
        if voice_client:
            print("Connected")
            await self.replay(voice_client)



        
load_dotenv()
BOTTOKEN = os.environ.get("BOTTOKEN")

bot.run(BOTTOKEN)
