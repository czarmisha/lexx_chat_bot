# import nltk
# from nltk.stem import WordNetLemmatizer
import spacy
from sqlalchemy import select
from db.models import Keyword, Topic


class AnalyzeQuestion():
    def __init__(self, session) -> None:
        self.topics = None
        self.session = session
        self.keywords = []
        self.set_keywords()

    def set_question(self, question):
        self.question = question

    def set_keywords(self):
        keywords = []
        stmt = select(Keyword)
        result = self.session.execute(stmt).scalars().all()
        print('!!!!!!!!!!!!!!!', 'set_keywords')
        for keyword in result:
            keywords.append(keyword.value)

        self.keywords = list(set(keywords))
        print('!!!!@@@@', self.keywords)

    def do_analyze(self):
        # # Создаем экземпляр лемматизатора
        # lemmatizer = WordNetLemmatizer()
        # # Лемматизируем ключевые слова
        # lemmatized_keywords = [lemmatizer.lemmatize(keyword.lower()) for keyword in self.keywords]
        # # Преобразуем текст вопроса в список отдельных слов
        # words = nltk.word_tokenize(self.question.lower())
        # # Ищем совпадения ключевых слов в тексте вопроса
        # matched_keywords = []
        # for keyword in lemmatized_keywords:
        #     keyword_words = nltk.word_tokenize(keyword)
        #     if all(word in words for word in keyword_words):
        #         matched_keywords.append(keyword)
        nlp = spacy.load("ru_core_news_sm")  # Загрузка предварительно обученной модели языка
        question_doc = nlp(self.question)

        matched_keywords = []
        for keyword in self.keywords:
            keyword_doc = nlp(keyword)

            if any(keyword_token.text.lower() in question_token.text.lower() for question_token in question_doc for keyword_token in keyword_doc):
                matched_keywords.append(keyword)

        self.matched_keywords = matched_keywords
        print('!!!!!!!!!!!!!!!matched_keywords', matched_keywords)
        return self.get_topics()
    
    def get_topics(self):
        stmt = select(Keyword).where(Keyword.value.in_(self.matched_keywords))
        result = self.session.execute(stmt).scalars().all()
        print('!!!!!!!', 'get_topics_1', result)
        ids = [keyword.topic_id for keyword in result]

        stmt = select(Topic).where(Topic.id.in_(ids))
        result = self.session.execute(stmt).scalars().all()
        print('!!!!!!!', 'get_topics_2', result)
        self.topics = {topic.name: topic.user_id for topic in result}
        return self.topics
