import pandas as pd
import os, inspect, sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import User, Topic, Session, engine
from sqlalchemy import select

df = pd.read_excel('flatfiles/test_topics.xlsx')
if not df.empty:
    session = Session(bind=engine)
    topics = df.columns.to_list()

    for topic in topics:
        if len(df[topic]) > 3:
            continue
        tg_id = int(df[topic][0])
        name = df[topic][1]
        city = df[topic][2]

        stmt = select(Topic).where(Topic.name==topic)
        result = session.execute(stmt).scalars().all()
        if result:
            print(f'Тема {topic} уже существует')
        else:
            stmt = select(User).where(User.tg_id==tg_id)
            user = session.execute(stmt).scalars().first()
            if not user:
                user = User(tg_id=tg_id, name=name, city=city)
                session.add(user)
                session.commit()
                print(f'create {name} {tg_id}')
            if city == 'Tashkent':
                topic = Topic(name=topic, tashkent_user_id=user.id)
            else:
                topic = Topic(name=topic, kyiv_user_id=user.id)

            session.add(topic)
            session.commit()
            print(f'create topic {topic}')

        

    session.close()