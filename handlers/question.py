import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, ForceReply
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)

from sqlalchemy import select
from db.models import Session, engine, User

session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

QUESTION, CLARIFICATION, ANSWER = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stmt = select(User).where(User.tg_id==int(user.id))
    result = session.execute(stmt).scalars().first()
    if not result:
        await update.message.reply_html(
            f"Привет {user.mention_html()}!\n У вас нет доступа. Обратитесь к администратору",
            reply_markup=ForceReply(selective=True),
        )

    await update.message.reply_html(
        f"Привет {user.mention_html()}!\nЗадайте мне свой вопрос",
        reply_markup=ForceReply(selective=True),
    )
    return QUESTION


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print('!!!!!', update.message)


async def clarification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def another_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        "Обращайтесь, если будут другие вопросы. Хорошего дня! \n🤔 /question \n🗣 /feedback"
    )


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}!\nЗадайте мне свой вопрос",
        reply_markup=ForceReply(selective=True),
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Обращайтесь, если будут другие вопросы. Хорошего дня! \n🤔 /question \n🗣 /feedback"
    )

    return ConversationHandler.END


conv_handler = ConversationHandler(
        entry_points=[CommandHandler('question', start)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question)],
            CLARIFICATION: [
                CallbackQueryHandler(clarification, pattern='^clarification_'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),],
            ANSWER: [
                CallbackQueryHandler(another_question, pattern='^another_question_yes$'),
                CallbackQueryHandler(finish, pattern='^another_question_no$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
