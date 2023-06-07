import pandas as pd
import os, inspect, sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import User, Session, engine
from sqlalchemy import select

df = pd.read_excel('flatfiles/test_users.xlsx')
if not df.empty:
    session = Session(bind=engine)
    
    for index, row in df.iterrows():
        tg_id = int(row['Telegram Id'])
        name = row['Name']

        stmt = select(User).where(User.tg_id==int(tg_id))
        result = session.execute(stmt).scalars().all()
        if result:
            print(f'{name} {tg_id} уже существует')
        else:
            user = User(tg_id=tg_id, name=name)
            session.add(user)
            session.commit()
            print(f'create {name} {tg_id}')

    session.close()