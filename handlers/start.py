import logging
from telegram import Update, ForceReply, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
)

from sqlalchemy import select
from db.models import Session, engine, User
from utils.keyboards import city_keyboard

session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

CITY = range(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stmt = select(User).where(User.tg_id==int(user.id))
    result = session.execute(stmt).scalars().first()
    if not result:
        await update.message.reply_html(
            f"Привет {user.mention_html()}!\n У вас нет доступа. Обратитесь к администратору",
            reply_markup=ForceReply(selective=True),
        )
    elif result and not result.chat_id:
        result.chat_id = update.effective_chat.id
        session.add(result)
        session.commit()

    if result.city:
        await update.message.reply_html(
            f"Привет {user.mention_html()}! Чем могу быть полезен? \n🤔 /question \n🗣 /feedback",
        )
        return ConversationHandler.END

    keyboard = city_keyboard()
    await update.message.reply_text("Выберите город", reply_markup=InlineKeyboardMarkup(keyboard))

    return CITY


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()
    user = update.effective_user
    stmt = select(User).where(User.tg_id==int(user.id))
    result = session.execute(stmt).scalars().first()
    city = query.data.split('_')[1]
    result.city = city
    session.add(result)
    session.commit()

    await query.edit_message_text(
        text=f"Привет {user.mention_html()}! Чем могу быть полезен? \n🤔 /question \n🗣 /feedback", parse_mode=ParseMode.HTML)

    return ConversationHandler.END


async def conv_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    query.answer()
    await query.edit_message_text(
        text="Обращайтесь, если будут другие вопросы. Хорошего дня! \n\n🤔 Задать вопрос: /question \n🗣 Оставить отзыв: /feedback"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Вы отменили регистрацию \nКоманда для регистрации - /start"
    )

    return ConversationHandler.END


start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CITY: [
                CallbackQueryHandler(city, pattern='^city_'),
                CallbackQueryHandler(conv_cancel, pattern='^cancel$'),],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
