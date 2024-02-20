import discord
from discord.ext import commands
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from models import Expense, engine

class DeleteSelectView(discord.ui.View):
    def __init__(self, timeout=180, records=None):
        super().__init__(timeout=timeout)
        self.records = records
        self.value = None

        self.add_item(Dropdown(self.records))
        self.add_item(EndButton())


class DeleteComfarmView(discord.ui.View):
    def __init__(self, timeout=180, value=None):
        self.value = value
        super().__init__(timeout=timeout)

    # アイテムたちを追加
        self.add_item(ConfarmButton(self.value))
        self.add_item(EndButton())


class Dropdown(discord.ui.Select):
    def __init__(self, records=None):
        self.records = records
        
        # optionsに選択肢を入れる
        options = []
        i = 1
        for record in self.records:
            options.append(discord.SelectOption(label=i, value=f'{record.id}', description=f'{record.oshi}のグッズ{record.goods_name}:￥{record.price}'))
            i += 1
        # Selectの作成
        super().__init__(placeholder='消したいやつ選んでね', min_values=1, max_values=1, options=options)
    
    # 選択されたときの処理
    async def callback(self, interaction: discord.Interaction):
        # 呼び出してきたビューを止める
        self.view.stop()

        # どんな内容か取ってくる
        options = interaction.message.components[0].children[0].options
        description = ""
        for option in options:
            if(int(self.values[0]) == int(option.value)):
                description = option.description
                print(description)

        # ビューを作る
        view = DeleteComfarmView(value=self.values[0])
        await interaction.response.edit_message(content=f"{description}を消してもいいですか",view=view)


class EndButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="end")
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="取り消したよ", view=None)
        self.view.stop()

class ConfarmButton(discord.ui.Button):
    def __init__(self, value = None):
        self.value = value
        super().__init__(style=discord.ButtonStyle.primary, label="confarm")
    
    async def callback(self, interaction: discord.Interaction):
        try:
            # セッション生成
            Session = sessionmaker(bind=engine)
            session = Session()
            # ユーザーIDでレコード検索
            record = session.query(Expense).filter_by(id = self.value).first()
            session.delete(record)
            session.commit()
            
        except Exception as e:
            # 何か例外が起こったらここで対応
            print(e)
            
        finally:
            # 絶対セッション閉じてから出ていく
            session.close()
        await interaction.response.edit_message(content=f"{record.oshi}のグッズ{record.goods_name}:￥{record.price}を消したよ！", view=None)
        self.view.stop()

        # 消し袂のメッセージ削除
        load_dotenv()
        channel_id = os.environ.get("CHANNEL_ID")
        channel = interaction.client.get_channel(int(channel_id))
        message = channel.get_partial_message(int(record.message_id))
        await message.delete()
