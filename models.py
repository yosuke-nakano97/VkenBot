import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.event import listen
from datetime import datetime
import pytz

Base = declarative_base()

class Expense(Base):
    __tablename__ = 'expence'

    id = Column(Integer, primary_key=True, autoincrement=True)
    goods_name = Column(String(length=255))
    user_id = Column(Integer, index=True)
    price = Column(Integer)
    oshi = Column(String(length=255))
    message_id = Column(Integer, default=0, index = True)
    created_at = Column(DateTime)

engine = sqlalchemy.create_engine('sqlite:///sample_db.sqlite3', echo=True)

Base.metadata.create_all(bind=engine)

def update_created_at(mapper, connection, target):
    if not target.created_at:
        target.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))

listen(Expense, 'before_insert', update_created_at)