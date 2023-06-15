import logging, datetime
from dotenv import load_dotenv
from telegram import Update, ForceReply, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)

from sqlalchemy import select
from db.models import Session, engine, User, Question, default_manager_td_id
from utils.analyze import AnalyzeQuestion
from utils.keyboards import (
    topic_choice_keyboard,
    another_question_keyboard,
)

session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

QUESTION, CLARIFICATION, ANSWER = range(3)
analyze = AnalyzeQuestion(session)


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
    stmt = select(User).where(User.tg_id==int(update.effective_user.id))
    author = session.execute(stmt).scalars().first()
    if not author:
        logger.info('error/ author is not find')
        update.message.reply_text("Произошел сбой в программе. Сообщите администратору")
        return ConversationHandler.END

    analyze.set_question(update.message.text)
    topics = analyze.do_analyze()
    if not topics:
        stmt = select(User).where(User.tg_id==int(default_manager_td_id))
        manager = session.execute(stmt).scalars().first()
        chat_id = manager.chat_id
        text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
               f"{analyze.question}"
        context.bot.send_message(chat_id=chat_id, text=text)
        keyboard = another_question_keyboard()
        update.message.reply_text("Нужный отдел поможет тебе с этим. Они уже получили ваш запрос и напишут вам в ближайшее время🙌🏼")
        update.message.reply_text("Есть ли у вас еще вопросы?", reply_markup=InlineKeyboardMarkup(keyboard))
        return ANSWER
    
    keyboard = topic_choice_keyboard(topics)
    update.message.reply_text(f"Уточните к какой теме относится ваш вопрос:", reply_markup=InlineKeyboardMarkup(keyboard))

    return CLARIFICATION


async def clarification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    stmt = select(User).where(User.tg_id==int(update.effective_user.id))
    author = session.execute(stmt).scalars().first()
    if not author:
        logger.info('error/ author is not find')
        update.message.reply_text("Произошел сбой в программе. Сообщите администратору")
        return ConversationHandler.END

    data = query.data.split('_')
    topic_id = data[1]
    user_id = data[-1]
    stmt = select(User).where(User.id==int(user_id))
    manager = session.execute(stmt).scalars().first()
    if not manager:
        stmt = select(User).where(User.tg_id==int(default_manager_td_id))
        manager = session.execute(stmt).scalars().first()
        chat_id = manager.chat_id
        text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
               f"{analyze.question}"
        context.bot.send_message(chat_id=chat_id, text=text)
    else:
        chat_id = manager.chat_id
        text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
               f"{analyze.question}"
        context.bot.send_message(chat_id=chat_id, text=text)
    
    question = Question(date=datetime.date.today(),
                        text=analyze.question,
                        topic_id=int(topic_id),
                        author_id=author.id,
                        )
    session.add(question)
    session.commit()

    keyboard = another_question_keyboard()
    update.message.reply_text("Нужный отдел поможет тебе с этим. Они уже получили ваш запрос и напишут вам в ближайшее время🙌🏼")
    update.message.reply_text("Есть ли у вас еще вопросы?", reply_markup=InlineKeyboardMarkup(keyboard))
    return ANSWER


async def another_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    await update.message.reply_html("Задайте мне свой вопрос")
    return QUESTION


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    await update.message.reply_html(
        "Обращайтесь, если будут другие вопросы. Хорошего дня! \n\n🤔 Задать вопрос: /question \n🗣 Оставить отзыв: /feedback"
    )

    return ConversationHandler.END


async def conv_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    query.answer()
    await update.message.reply_text(
        "Обращайтесь, если будут другие вопросы. Хорошего дня! \n\n🤔 Задать вопрос: /question \n🗣 Оставить отзыв: /feedback"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Обращайтесь, если будут другие вопросы. Хорошего дня! \n\n🤔 Задать вопрос: /question \n🗣 Оставить отзыв: /feedback"
    )

    return ConversationHandler.END


question_handler = ConversationHandler(
        entry_points=[CommandHandler('question', start)],
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
