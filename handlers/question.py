import logging
from telegram import Update, ForceReply
from telegram.ext import ContextTypes, MessageHandler, filters

from sqlalchemy import select
from db.models import Session, engine, User

session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stmt = select(User).where(User.tg_id==int(user.id))
    result = session.execute(stmt).scalars().first()
    if not result:
        await update.message.reply_html(
            f"Привет {user.mention_html()}!\n У тебя нет доступа. Обратись к администратору",
            reply_markup=ForceReply(selective=True),
        )

    await update.message.reply_html(
        f"Привет {user.mention_html()}!\nЗадай мне свой вопрос",
        reply_markup=ForceReply(selective=True),
    )

question_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, question)
