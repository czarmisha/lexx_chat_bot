import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger

_BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(_BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

_db_filename = os.environ['DB_FILENAME']
db_path = os.path.join(_BASE_DIR, _db_filename)
engine = create_engine(f'sqlite:///{db_path}.db', echo=True)
default_manager_tashkent = os.environ['DEFAULT_MANAGER_KYIV']
default_manager_kyiv = os.environ['DEFAULT_MANAGER_TASHKENT']

Base = declarative_base()
Session = sessionmaker()


class Topic(Base):
    __tablename__ = 'topic'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    tashkent_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    kyiv_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    tashkent_user = relationship("User", back_populates="tashkent_topics", foreign_keys=[tashkent_user_id])
    kyiv_user = relationship("User", back_populates="kyiv_topics", foreign_keys=[kyiv_user_id])
    question = relationship("Question", back_populates="topic")
    keyword = relationship("Keyword", back_populates="topic")

    def __repr__(self):
        return f'<Topic: {self.name}>'
    

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=True)
    city = Column(String(80), nullable=True)
    name = Column(String(80), nullable=False)

    tashkent_topics = relationship("Topic", back_populates="tashkent_user", foreign_keys="Topic.tashkent_user_id")
    kyiv_topics = relationship("Topic", back_populates="kyiv_user", foreign_keys="Topic.kyiv_user_id")
    question = relationship("Question", back_populates="author")

    def __repr__(self):
        return f'<User - {self.name}, id: {self.id}>'


class Keyword(Base):
    __tablename__ = 'keyword'

    id = Column(Integer, primary_key=True)
    value = Column(String(255), nullable=False)
    
    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship("Topic", back_populates="keyword")

    def __repr__(self):
        return f'<Keyword {self.value}>'


class Question(Base):
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    text = Column(String(255), nullable=False)

    topic_id = Column(Integer, ForeignKey("topic.id"))
    topic = relationship("Topic", back_populates="question")
    author_id = Column(Integer, ForeignKey("user.id"))
    author = relationship("User", back_populates="question")

    def __repr__(self):
        return f'<Question: {self.author_firstname} {self.text}>'
    

class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return f'<Channel {self.name}>'