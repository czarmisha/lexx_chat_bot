import nltk
from nltk.stem import WordNetLemmatizer
from sqlalchemy import select
from db.models import Keyword, Topic

# Исходный текст вопроса и список ключевых слов
question = "Ваш вопрос"
keywords = ["ключевое слово 1", "ключевое слово 2", "ключевое слово 3"]

# Создаем экземпляр лемматизатора
lemmatizer = WordNetLemmatizer()

# Лемматизируем ключевые слова
lemmatized_keywords = [lemmatizer.lemmatize(keyword.lower()) for keyword in keywords]

# Преобразуем текст вопроса в список отдельных слов
words = nltk.word_tokenize(question.lower())

# Ищем совпадения ключевых слов в тексте вопроса
matched_keywords = []
for keyword in lemmatized_keywords:
    keyword_words = nltk.word_tokenize(keyword)
    if all(word in words for word in keyword_words):
        matched_keywords.append(keyword)

# Выводим найденные ключевые слова
print(matched_keywords)
class AnalyzeQuestion():
    def __init__(self, question, session) -> None:
        self.session = session
        self.question = question
        self.keywords = []
        self.set_keyword()

    def set_keywords(self):
        keyword = []
        stmt = select(Keyword)
        result = self.session.execute(stmt).scalars().all()
        print('!!!!!!!!!!!!!!!', 'set_keywords')
        for keyword in result:
            print('@', keyword.value)
            keywords.append(keyword)

        self.keywords = list(set(keywords))

    def do_analyze(self):
        # Создаем экземпляр лемматизатора
        lemmatizer = WordNetLemmatizer()
        # Лемматизируем ключевые слова
        lemmatized_keywords = [lemmatizer.lemmatize(keyword.lower()) for keyword in self.keywords]
        # Преобразуем текст вопроса в список отдельных слов
        words = nltk.word_tokenize(self.question.lower())
        # Ищем совпадения ключевых слов в тексте вопроса
        matched_keywords = []
        for keyword in lemmatized_keywords:
            keyword_words = nltk.word_tokenize(keyword)
            if all(word in words for word in keyword_words):
                matched_keywords.append(keyword)
        
        self.matched_keywords = matched_keywords
        return self.get_topics()
    
    def get_topics(self):
        stmt = select(Keyword).where(Keyword.value.in_(self.matched_keywords))
        result = self.session.execute(stmt).scalars().all()
        ids = [keyword.topic_id for keyword in result]

        stmt = select(Topic).where(Topic.id.in_(ids))
        result = self.session.execute(stmt).scalars().all()
        self.topics = {topic.name: topic.user_id for topic in result}
        return self.topics
