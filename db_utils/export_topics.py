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
        tashkent_user_id = None
        kyiv_user_id = None
        if len(df[topic]) > 7:
            print(f'len of column {topic} too long')
            continue

        df_users = []
        df_users.append({
            'tg_id': int(df[topic][0]),
            'name': df[topic][1],
            'city': df[topic][2],
        })
        df_users.append({
            'tg_id': int(df[topic][4]),
            'name': df[topic][5],
            'city': df[topic][6],
        })

        for df_user in df_users:
            stmt = select(User).where(User.tg_id==df_user['tg_id'])
            user = session.execute(stmt).scalars().first()
            if not user:
                user = User(
                    tg_id=df_user['tg_id'],
                    name=df_user['name'],
                    city=df_user['city']
                )
                session.add(user)
                session.commit()
                print(f"create {df_user['name']} {df_user['tg_id']}")
            if df_user['city'] == 'Tashkent':
                tashkent_user_id = user.id
            else:
                kyiv_user_id = user.id

        stmt = select(Topic).where(Topic.name==topic)
        result = session.execute(stmt).scalars().all()
        if result:
            print(f'Тема {topic} уже существует')
            result.tashkent_user_id = tashkent_user_id
            result.kyiv_user_id = kyiv_user_id
            session.add(result)
            session.commit()
        else:
            topic = Topic(
                name=topic,
                tashkent_user_id=user.id,
                kyiv_user_id=kyiv_user_id
            )
            session.add(topic)
            session.commit()
            print(f'create topic {topic}')

    session.close()