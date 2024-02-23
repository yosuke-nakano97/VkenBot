import discord
from discord.ext import commands
from discord import app_commands
import os, random, datetime, asyncio


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 音楽流してるとTrueにする
        self.playing_flag = False
        # ボイチャに入っていたらTrue
        self.connected_flag = False

    # joinコマンド
    @app_commands.command(name="join")
    async def join(self, intr):
        print("join")
        # ボットなら無視
        if intr.user.bot:
            await intr.response.send_message("あんたBot", ephemeral = True)
            return
        # 送った人がボイチャにいるか
        if intr.user.voice:
            channel = intr.user.voice.channel
            voice_channel = discord.utils.get(self.bot.voice_clients, guild=intr.guild)
            print(voice_channel)

            if not voice_channel:
                self.connected_flag = True
                # ボイスチャンネルに接続していない場合は接続する
                vc = await channel.connect(timeout=30.0, self_deaf=True)
                print(f"Connected to {channel}")
                await intr.response.send_message("やっほー", ephemeral = True)
            else:
                # しているとそのまま何も起こらない
                await intr.response.send_message("もう入ってるじゃん", ephemeral = True)
        else:
            # していない場合
            print("You don't connect to a voice channel")
            await intr.response.send_message("どこにはいればいいかわからないよ", ephemeral = True)

    # # leaveコマンド
    @app_commands.command(name="leave")
    async def leave(self, intr):
            print("leave")
            # ボットなら無視
            if intr.user.bot:
                await intr.response.send_message("あんたbot", ephemeral = True)
                return
            # ボイチャに入ってなかったら
            if intr.user.voice is None:
                await intr.response.send_message("ボイチャ入ってないじゃん", ephemeral = True)
                print("you dont connect to a voice channel")
                return

            voice_channel = discord.utils.get(self.bot.voice_clients, guild=intr.guild)
            print(voice_channel)
            
            if voice_channel.channel == intr.user.voice.channel:
                
                # ボイスチャンネルにしてたら切る
                await voice_channel.disconnect()
                self.connected_flag = False

                print(f"Disconnected from {voice_channel}")
                await intr.response.send_message("ばいばいー", ephemeral = True)
            else:
                # ボイスチャンネルに入ってなかったら無視
                print("You don't connect to a voice channel.")
                await intr.response.send_message("あんたこのボイチャ入ってないじゃん", ephemeral = True)
    # playコマンド
    @app_commands.command(name="play")
    async def play(self, intr):
        print("play")
        # ボットなら無視
        if intr.user.bot:
            return
            await intr.response.send_message("あんたbot", ephemeral = True)
        # ユーザーがボイチャにいなければ無視
        if intr.user.voice is None:
            await intr.response.send_message("ボイチャ入ってないじゃん", ephemeral = True)
            print("you dont connect to a voice channel")
            return

        voice_channel = discord.utils.get(self.bot.voice_clients, guild=intr.guild)
        # ボイチャに入っていなければ無視
        if voice_channel is None or not voice_channel.is_connected():
            await intr.response.send_message("ボイチャ入ってないじゃん", ephemeral = True)
            return

        #   playig(２回以上してたらTrue)で１回目じゃないと無視 
        if self.playing_flag:
            await intr.response.send_message("もう流してるよ", ephemeral = True)
            return

        try:
            # 1度入ると記憶
            self.playing_flag = True

            # インタラクションの処理
            await intr.response.send_message("OK！", ephemeral = True)

            # 音を出す所に入る
            await self.play_music(voice_channel)

        except discord.errors.ClientException as e:
            print(f"Error in play command: {e}")
        finally:
            # メソッドが終わるとFalseに
            self.playing_flag = False
            print("fin")
                        

    async def play_music(self, voice_channel):
        # ファイル群の名前をもらってくる
        current_directory = os.path.dirname(os.path.realpath(__file__))
        target_directory = os.path.join(current_directory, "..", "musics")
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
                channel_state = discord.utils.get(self.bot.voice_clients, guild=voice_channel.guild)

                # もしボイスチャンネルが変更されたらループを抜ける
                if channel_state and channel_state.channel.id != voice_channel.channel.id:
                    voice_channel.stop()
                    return
            print("playend")

    async def replay(self, channel):
        #   playig(２回以上してたらTrue)で１回目じゃないと無視 
        if self.playing_flag:
            return

        try:
            # 1度入ると記憶
            self.playing_flag = True
            # 音を出す所に入る
            await self.play_music(channel)
        except discord.errors.ClientException as e:
            print(f"Error in play command: {e}")
        finally:
            # メソッドが終わるとFalseに
            self.playing_flag = False 

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f"on_voice_state_update:member:{member},before{before},after:{after}")

        if member.name != self.bot.user.name:
            print("no")
            return
        
        if not before.channel:
            print("first")
            return

        if not self.connected_flag:
            print("flag_off!")
            return

        print("yes")
        await asyncio.sleep(40)

        previous_channel = before.channel
        voice_client = discord.utils.get(self.bot.voice_clients, channel=previous_channel)
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
            if self.playing_flag:
                await self.replay(voice_client)

async def setup(bot: commands.Bot): 
        await bot.add_cog(MusicCog(bot))
