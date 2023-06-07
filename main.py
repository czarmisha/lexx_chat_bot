import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from handlers import start

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token = os.environ['BOT_TOKEN']

if __name__ == '__main__':
    application = Application.builder().token(token).build()
    application.add_handler(start.start_handler)

    # dispatcher.add_handler(repair.repair_handler)
    # dispatcher.add_handler(reserve.reserve_handler)
    # dispatcher.add_handler(initiate.initiate_handler)
    # dispatcher.add_handler(display.display_handler)
    # dispatcher.add_handler(display.option_handler)
    # dispatcher.add_handler(my_events.my_events_handler)
    # dispatcher.add_handler(my_events.event_handler)
    # dispatcher.add_handler(my_events.del_handler)
    # dispatcher.add_handler(my_events.edit_handler)
    # dispatcher.add_handler(feedback.feedback_handler)
    # dispatcher.add_handler(help.help_handler)

    # dispatcher.add_error_handler(error.UnauthorizedError)

    application.run_polling(allowed_updates=Update.ALL_TYPES)
