from models import engine, User, Expense
from sqlalchemy.orm import sessionmaker


def monthly_initialize():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        records = session.query(User).all()
        for user in records:
            user.last_month_use = user.month_use
            user.month_use = 0
        session.commit()
    except Exception as e:
        print(e)

    finally:
        session.close()

def anual_initialize():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        records = session.query(User).all()
        for user in records:
            user.last_year_use = user.year_use
            user.year_use = 0
        session.commit()
    except Exception as e:
        print(e)

    finally:
        session.close()