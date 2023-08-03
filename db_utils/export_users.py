import pandas as pd
import os, inspect, sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import User, Session, engine
from sqlalchemy import select

df = pd.read_excel('flatfiles/users.xlsx')
if not df.empty:
    session = Session(bind=engine)
    
    for index, row in df.iterrows():
        tg_id = int(row['Telegram Id'])
        name = row['Name']
        city = row['Office']
        type = row['Type']

        stmt = select(User).where(User.tg_id==int(tg_id))
        user = session.execute(stmt).scalars().first()
        if user:
            print(f'{name} {tg_id} уже существует. Обновляю')
            user.name = name
            user.city = city
            user.type = type
        else:
            user = User(
                tg_id=tg_id,
                name=name,
                city=city,
                type=type
            )
            print(f'Создаю {name} {tg_id}')
        
        session.add(user)
        session.commit()

    session.close()