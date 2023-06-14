import nltk
from nltk.stem import WordNetLemmatizer

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
    def __init__(self, question) -> None:
        self.question = question
        self.keywords = []
        self.set_keyword()

    def set_keywords(self):
        pass

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

        return self.get_themes()
    
    def get_themes(self):
        pass
