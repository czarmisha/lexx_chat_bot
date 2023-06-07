import pandas as pd
import os, inspect, sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import User, Topic, Keyword, Session, engine
from sqlalchemy import select

df = pd.read_excel('flatfiles/test_keywords.xlsx')
if not df.empty:
    session = Session(bind=engine)
    topics = df.columns.to_list()

    for topic in topics:
        if df[topic].empty:
            continue
        
        keywords = df[topic].to_list()
        for keyword in keywords:
            if keyword == '' or pd.isna(keyword):
                continue
            stmt = select(Topic).where(Topic.name==topic)
            curr_topic = session.execute(stmt).scalars().first()
            if not curr_topic:
                print(f'Тема {topic} не существует')
                continue
            stmt = select(Keyword).where(Keyword.value==keyword, Keyword.topic_id==curr_topic.id)
            curr_keyword = session.execute(stmt).scalars().first()
            if not curr_keyword:
                curr_keyword = Keyword(value=keyword, topic_id=curr_topic.id)
                session.add(curr_keyword)
                session.commit()
                print(f'create keyword {keyword} for topic {topic}')

    session.close()