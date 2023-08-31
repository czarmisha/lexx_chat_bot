import logging
from telegram import Update, ForceReply
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters
)

from sqlalchemy import select
from db.models import (
    Session,
    engine,
    User,
    default_manager_tashkent,
    default_manager_kyiv,
)

session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TEXT = range(1)
# TODO: спросить имя при старте

async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stmt = select(User).where(User.tg_id==int(user.id))
    author = session.execute(stmt).scalars().first()
    if not author:
        await update.message.reply_html(
            f"Привет {user.mention_html()}!\n У вас нет доступа. Обратитесь к администратору",
            reply_markup=ForceReply(selective=True),
        )
        return ConversationHandler.END
        
    elif author and not author.chat_id:
        await update.message.reply_html(
            f"Привет {user.mention_html()}!\nВы не прошли регистрацию. Пожалуйста, пройдите ее \nКоманда для регистрации - /start",
            reply_markup=ForceReply(selective=True),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Напишите мне свой отзыв/проблему и тд.",
        reply_markup=ForceReply(selective=True),
    )
    return TEXT


async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stmt = select(User).where(User.tg_id==int(update.effective_user.id))
    author = session.execute(stmt).scalars().first()
    if not author:
        logger.info('error/ author is not find')
        await update.message.reply_html(
            f"Привет {update.effective_user.mention_html()}!\n У вас нет доступа. Обратитесь к администратору",
            reply_markup=ForceReply(selective=True),
        )
    
    mess_text = update.message.text

    if author.city == 'Tashkent':
        stmt = select(User).where(User.tg_id==int(default_manager_tashkent))
    else:
        stmt = select(User).where(User.tg_id==int(default_manager_kyiv))

    manager = session.execute(stmt).scalars().first()
    chat_id = manager.chat_id
    text = f"Новый отзыв от {author.name}({author.tg_id})\n\n" \
            f"{mess_text}"
    await context.bot.send_message(chat_id=chat_id, text=text)
    
    await update.message.reply_text("Спасибо за отзыв! Продолжим?\n\n🤔 Задать вопрос: /question \n🗣 Оставить отзыв: /feedback")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Обращайтесь, если будут другие вопросы. Хорошего дня!\nКоманда для регистрации - /start"
    )

    return ConversationHandler.END


feedback_handler = ConversationHandler(
        entry_points=[CommandHandler('feedback', feedback)],
        states={
            TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
