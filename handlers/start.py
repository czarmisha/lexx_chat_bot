import logging
from telegram import Update, ForceReply
from telegram.ext import ContextTypes, CommandHandler

from sqlalchemy import select
from db.models import Session, engine, User

session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stmt = select(User).where(User.tg_id==int(user.id))
    result = session.execute(stmt).scalars().first()
    if not result:
        await update.message.reply_html(
            f"Привет {user.mention_html()}!\n У тебя нет доступа. Обратись к администратору",
            reply_markup=ForceReply(selective=True),
        )

    await update.message.reply_html(
        f"Привет {user.mention_html()}! Чем могу быть полезен? \n🤔 /question \n🗣 /feedback",
        reply_markup=ForceReply(selective=True),
    )

start_handler = CommandHandler('start', start)

start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question)],
            CLARIFICATION: [
                CallbackQueryHandler(clarification, pattern='^clarification_'),
                CallbackQueryHandler(conv_cancel, pattern='^cancel$'),],
            ANSWER: [
                CallbackQueryHandler(another_question, pattern='^another_question_yes$'),
                CallbackQueryHandler(finish, pattern='^another_question_no$'),
                CallbackQueryHandler(conv_cancel, pattern='^cancel$'),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
