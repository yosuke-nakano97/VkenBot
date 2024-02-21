import discord
from discord.ext import commands
from discord import app_commands
import re
from datetime import datetime, timedelta ,timezone
from sqlalchemy.orm import sessionmaker
from models import Expense, User, engine
from cogs.views.deleteview import DeleteSelectView
from cogs.views.detailview import JumpView

class MoneyTrackCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="use")
    async def use(self, intraction, item: str, price: str, oshi: str):
        # priceを正の数値に
        price = self.validateValue(intraction, price)
        if price is not None:
            # 記録して返り値を取る
            result = await self.TrackRegester(intraction, item, price, oshi)
            if result != 0:
                # 正常終了の場合
                await intraction.response.send_message(f"{oshi}のグッズ{item}:￥{price}")
                message = await intraction.original_response()
                self.MessageIdRegester(result, message.id)
            else:
                # 異常終了のお知らせ
                await intraction.response.send_message("何かがおかしいよ‼再登録して‼")
        else:
            # 式がおかしかったり、負の数を入れると警告
            await intraction.response.send_message(f"priceの値がおかしいよ!",ephemeral = True)
            
    @app_commands.command(name="delete")
    async def delete(self, intraction):
        user_id = intraction.user.id
        try:
            # セッション生成
            Session = sessionmaker(bind=engine)
            session = Session()
            # ユーザーIDでレコード検索
            records = session.query(Expense).filter_by(user_id=user_id).limit(25)
            
            print(records)
            
        except Exception as e:
            # 何か例外が起こったらここで対応
            print(e)
            
        finally:
            # 絶対セッション閉じてから出ていく
            session.close()

        print(records)
        view = DeleteSelectView(records=records)
        await intraction.response.send_message("消したいの選んでね(直近25個表示)",view = view, ephemeral = True, delete_after = 170)

    @app_commands.command(name="month")
    async def month(self, intraction, member:discord.Member):
        user_id = member.id
        try:
            Session = sessionmaker(bind=engine)
            session = Session()
            record = session.query(User).filter_by(id=user_id).first()
            if record:
                if record.month_use != 0:
                    await intraction.response.send_message(f"{member.name}の今月の出費は{record.month_use}だよ！")
            else:
                await intraction.response.send_message(f"まだ今月は出費がないよ！")

        except Exception as e:
            print(e)
            await intraction.response.send_message(f"なんかおかしいみたい！")

        finally:
            session.close()

    @app_commands.command(name="year")
    async def year(self, intraction, member:discord.Member):
        user_id = member.id
        try:
            Session = sessionmaker(bind=engine)
            session = Session()
            record = session.query(User).filter_by(id=user_id).first()
            if record:
                if record.month_use != 0:
                    await intraction.response.send_message(f"{member.name}の今年の出費は{record.year_use}だよ！")
            else:
                await intraction.response.send_message(f"まだ今年は出費がないよ！")

        except Exception as e:
            print(e)
            await intraction.response.send_message(f"なんかおかしいみたい！")

        finally:
            session.close()

    @app_commands.command(name="total")
    async def total(self, intraction, member:discord.Member):
        user_id = member.id
        try:
            Session = sessionmaker(bind=engine)
            session = Session()
            record = session.query(User).filter_by(id=user_id).first()
            if record:
                if record.month_use != 0:
                    await intraction.response.send_message(f"{member.name}の今年の出費は{record.total_use}だよ！")
            else:
                await intraction.response.send_message(f"まだ出費がないよ！")

        except Exception as e:
            print(e)
            await intraction.response.send_message(f"なんかおかしいみたい！")

        finally:
            session.close()

    @app_commands.command(name="detail")
    async def detail(self, intraction):
        view = JumpView()
        await intraction.response.send_message("これ押して！",view=view)
        pass

    async def TrackRegester(self, intraction, item, price, oshi): 
        try:
            user_id = intraction.user.id
            # セッション生成
            Session = sessionmaker(bind=engine)
            session = Session()
            # Expenseレコード作成
            newtrack = Expense(goods_name=item, user_id=user_id, price=price, oshi=oshi)

            # useidからユーザーがすでにレコードを持ってるか確認
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                # もってたら追加
                user.month_use += price
                user.year_use += price
                user.total_use += price
            else:
                # 持ってなかったら登録
                newuser = User(id=user_id, month_use=price, year_use=price, total_use=price)
                session.add(newuser)

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