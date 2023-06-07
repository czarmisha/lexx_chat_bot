import pandas as pd
import os, inspect, sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import User, Session, engine

df = pd.read_excel('flatfiles/test_users.xlsx')
if not df.empty:
    session = Session(bind=engine)
    
    for index, row in df.iterrows():
        tg_id = row['Telegram Id']
        name = row['Name']
        print('!!!!!!!!!!!!!!!!!!!!!!'*3, tg_id, name)
    
        user_exists = session.query(User).filter(User.tg_id == tg_id).first() is not None
        if user_exists:
            print(f'{name} {tg_id} уже существует')
        else:
            user = User(tg_id=tg_id, name=name)
            session.add(user)
            session.commit()
            print(f'create {name} {tg_id}')

    session.close()