import pandas as pd
import os, inspect, sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from db.models import Channel, Session, engine
from sqlalchemy import select

df = pd.read_excel('flatfiles/channels.xlsx')
if not df.empty:
    session = Session(bind=engine)
    channels = df['Channel name'].to_list()
    print(channels)
    
    for channel_name in channels:
        stmt = select(Channel).where(Channel.name==channel_name)
        result = session.execute(stmt).scalars().all()
        if result:
            print(f'Канал {channel_name} уже существует')
        else:
            channel = Channel(name=channel_name)
            session.add(channel)
            session.commit()
            print(f'Create channel {channel_name}')

    session.close()