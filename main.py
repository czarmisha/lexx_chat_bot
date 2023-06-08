import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application

from handlers import start, question

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token = os.environ['BOT_TOKEN']

if __name__ == '__main__':
    application = Application.builder().token(token).build()
    application.add_handler(start.start_handler)
    application.add_handler(question.question_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
