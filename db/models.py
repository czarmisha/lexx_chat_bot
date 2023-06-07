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

Base = declarative_base()
Session = sessionmaker()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, nullable=False)
    name = Column(String(80), nullable=False)

    topic = relationship("Topic", back_populates="user")
    question = relationship("Question", back_populates="author")

    def __repr__(self):
        return f'<User - {self.name}, id: {self.id}>'


class Topic(Base):
    __tablename__ = 'topic'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="topic")
    question = relationship("Question", back_populates="topic")
    keyword = relationship("Keyword", back_populates="topic")

    def __repr__(self):
        return f'<Topic: {self.name}>'


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