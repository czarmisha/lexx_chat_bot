import pandas as pd
import os, inspect, sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import User, Topic, Session, engine
from sqlalchemy import select

df = pd.read_excel('flatfiles/topics.xlsx')
if not df.empty:
    session = Session(bind=engine)

    for index, row in df.iterrows():
        name = row['Name']
        tashkent_manager_name = row['Tmanager name']
        tashkent_manager_td_id = row['Tmanager tg_id']
        kyiv_manager_name = row['Kmanager name']
        kyiv_manager_td_id = row['Kmanager tg_id']
        url_answer = row['URL answer']

        if not pd.notna(name):
            continue

        tashkent_manager = None
        if pd.notna(tashkent_manager_td_id):
            stmt = select(User).where(User.tg_id==tashkent_manager_td_id)
            tashkent_manager = session.execute(stmt).scalars().first()
            if not tashkent_manager:
                tashkent_manager = User(
                    tg_id=tashkent_manager_td_id,
                    name=tashkent_manager_name,
                    city='Tashkent'
                )
                session.add(tashkent_manager)
                session.commit()
                print(f"create Tashkent manager {tashkent_manager_name} {tashkent_manager_td_id} for topic {name}")
        
        kyiv_manager = None
        if pd.notna(kyiv_manager_td_id):
            stmt = select(User).where(User.tg_id==kyiv_manager_td_id)
            kyiv_manager = session.execute(stmt).scalars().first()
            if not kyiv_manager:
                kyiv_manager = User(
                    tg_id=kyiv_manager_td_id,
                    name=kyiv_manager_name,
                    city='Tashkent'
                )
                session.add(kyiv_manager)
                session.commit()
                print(f"create Kyiv manager {kyiv_manager_name} {kyiv_manager_td_id} for topic {name}")

        
        stmt = select(Topic).where(Topic.name==name)
        result = session.execute(stmt).scalars().all()
        if result:
            print(f'Тема {name} уже существует')
            result.tashkent_user_id = tashkent_manager.id if tashkent_manager else None
            result.kyiv_user_id = kyiv_manager.id if kyiv_manager else None
            result.url_answer = url_answer
            session.add(result)
            session.commit()
        else:
            topic = Topic(
                name=name,
                tashkent_user_id=tashkent_manager.id if tashkent_manager else None,
                kyiv_user_id=kyiv_manager.id if kyiv_manager else None,
                url_answer=url_answer
            )
            session.add(topic)
            session.commit()
            print(f'create topic {name}')
                
    session.close()