import discord
from discord.ext import commands
from discord import app_commands
import re
from sqlalchemy.orm import sessionmaker
from models import Expense, engine
from cogs.views.deleteview import DeleteSelectView

class MoneyTrackCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="use")
    async def use(self, intraction, item: str, price: str, oshi: str):
        # priceを正の数値に
        price = self.validateValue(intraction, price)
        if price is not None:
            # 記録して返り値を取る
            result = self.TrackRegester(intraction, item, price, oshi)
            if result != 0:
                # 正常終了の場合
                await intraction.response.send_message(f"{oshi}のグッズ{item}:￥{price}")
                message = await intraction.original_response()
                self.MessageIdRegester(result, message.id)
            else:
                # 異常終了のお知らせ
                intraction.response.send_messeage("何かがおかしいよ‼再登録して‼")
        else:
            # 式がおかしかったり、負の数を入れると警告
            await intraction.response.send_message(f"priceの値がおかしいよ!",ephemeral = True)
            

    async def TrackRegester(self, intraction, item, price, oshi): 
        try:
            # セッション生成
            Session = sessionmaker(bind=engine)
            session = Session()
            # レコード作成
            newtrack = Expense(goods_name=item, user_id=intraction.user.id, price=price, oshi=oshi)
            # レコードをDBに追加
            session.add(newtrack)
            session.commit()
            last_record_id = session.query(Expense).order_by(Expense.id.desc()).first().id
            result = last_record_id

        except Exception as e:
            # 何か例外が起こったらここで対応
            result = 0
            print(e)
            
        finally:
            # 絶対セッション閉じてから出ていく
            session.close()
            return result

    def MessageIdRegester(self, id, message_id):
        try:
            # セッション生成
            Session = sessionmaker(bind=engine)
            session = Session()
            # レコード探してメッセージID入れる
            update = session.query(Expense).filter_by(id=id).one()
            update.message_id = message_id
            session.commit()

        except Exception as e:
            # 何か例外が起こったらここで対応
            print(e)
        
        finally:
            # 絶対セッション閉じてから出ていく
            session.close()
 
    def validateValue(self, intraction, input):
        print(input)
        # 許可する演算子
        allowed_operators = {'+', '-', '*', '/'}
        result = -1
        try:
            # inputが数字と+-*/の繰り返しの式か判定
            input_formula = re.findall('((([0-9]+[+\-\*\/])*)[0-9]*)', input)
            if input == input_formula[0][0]:
                result = eval(input)
                
            # inputの末尾が⁼=数字になっているかか確認
            input_equal = re.findall('(=[0-9]+$)', input)
            if input_equal:
                if input == str(input_formula[0][0]) + str(input_equal[0]):
                    s = str(input_equal[0])
                    index_of_equal_sign = s.index("=")
                    result = int(s[index_of_equal_sign + 1:])

            # 登録する額resultが正の値か確認
            if(result > 0):
                return result
            else:
                return None

        except (SyntaxError, ValueError):
            return None

async def setup(bot: commands.Bot): 
        await bot.add_cog(MoneyTrackCog(bot))