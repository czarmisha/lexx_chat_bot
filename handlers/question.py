import logging, datetime
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
from db.models import (
    Session,
    Topic,
    engine,
    User,
    Question,
    Channel,
    default_manager_tashkent,
    default_manager_kyiv,
)
from utils.analyze import AnalyzeQuestion
from utils.keyboards import (
    topic_choice_keyboard,
    another_question_keyboard,
    channel_choice_keyboard,
)

session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

QUESTION, CLARIFICATION, CHANNEL, ANSWER = range(4)
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
        return ConversationHandler.END
        
    elif result and not result.chat_id:
        await update.message.reply_html(
            f"Привет {user.mention_html()}!\nВы не прошли регистрацию \nКоманда для регистрации - /start",
            reply_markup=ForceReply(selective=True),
        )
        return ConversationHandler.END

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
        await update.message.reply_text("Произошел сбой в программе. Сообщите администратору")
        return ConversationHandler.END

    analyze.set_question(update.message.text)
    topics = analyze.do_analyze()
    if not topics:
        if author.city == 'Tashkent':
            stmt = select(User).where(User.tg_id==int(default_manager_tashkent))
        else:
            stmt = select(User).where(User.tg_id==int(default_manager_kyiv))

        manager = session.execute(stmt).scalars().first()
        if not manager:
            logger.info('error/ manager is not find')
            await update.message.reply_text("Произошла ошибка, обратитесь к администратору")
            return ConversationHandler.END
        elif manager and not manager.chat_id:
            logger.info('error/ manager chat_id is not find')
            await update.message.reply_text("Произошла ошибка, обратитесь к администратору")
            return ConversationHandler.END

        chat_id = manager.chat_id
        text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
               f"{analyze.question}\n\n" \
               f"Тема не найдена"
        await context.bot.send_message(chat_id=chat_id, text=text)
        keyboard = another_question_keyboard()
        await update.message.reply_text("Нужный отдел поможет тебе с этим. Они уже получили ваш запрос и напишут вам в ближайшее время🙌🏼")
        await update.message.reply_text("Есть ли у вас еще вопросы?", reply_markup=InlineKeyboardMarkup(keyboard))
        return ANSWER
    
    if len(topics) == 1:
        # TODO: если топик особый (требуется другой ответ типа ссылки и тд) то добавить этот функционал
        searched_topic = topics[0]
        if author.city == 'Tashkent':
            stmt = select(User).where(User.id==int(searched_topic['tashkent_user_id']))
        else:
            stmt = select(User).where(User.id==int(searched_topic['kyiv_user_id']))

        manager = session.execute(stmt).scalars().first()
        if not manager:
            logger.info('error/ manager is not find')
            await update.message.reply_text("Произошла ошибка, обратитесь к администратору")
            return ConversationHandler.END
        elif manager and not manager.chat_id:
            logger.info('error/ manager chat_id is not find')
            await update.message.reply_text("Произошла ошибка, обратитесь к администратору")
            return ConversationHandler.END

        if searched_topic['topic'] == 'Каналы':
            context.chat_data['manager_chat_id'] = manager.chat_id
            context.chat_data['author_name'] = author.name
            context.chat_data['author_tg_id'] = author.tg_id
            context.chat_data['author_id'] = author.id
            context.chat_data['topic_id'] = searched_topic['topic_id']
            stmt = select(Channel)
            channels = session.execute(stmt).scalars().all()
            channel_values = [{'id': channel.id, 'name': channel.name} for channel in channels]
            keyboard = channel_choice_keyboard(channel_values)
            await update.message.reply_text(f"Уточните в какой канал вас добавить:", reply_markup=InlineKeyboardMarkup(keyboard))
            return CHANNEL

        elif searched_topic['url']:
            chat_id = manager.chat_id
            text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
                f"{analyze.question}\n\nСсылка на ресурс уже отправлена пользователю"
            await context.bot.send_message(chat_id=chat_id, text=text)
            question = Question(date=datetime.date.today(),
                        text=analyze.question,
                        topic_id=int(searched_topic['topic_id']),
                        author_id=author.id,
                        )
            session.add(question)
            session.commit()
            keyboard = another_question_keyboard()
            await update.message.reply_text(f"Ответы по вашему вопросу уже есть по этой ссылке:\n{searched_topic['url']}")
            await update.message.reply_text("Есть ли у вас еще вопросы?", reply_markup=InlineKeyboardMarkup(keyboard))
            return ANSWER
            
        chat_id = manager.chat_id
        text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
               f"{analyze.question}\n\n" \
               f"Тема: {searched_topic['topic']}"
        await context.bot.send_message(chat_id=chat_id, text=text)
        question = Question(date=datetime.date.today(),
                        text=analyze.question,
                        topic_id=int(searched_topic['topic_id']),
                        author_id=author.id,
                        )
        session.add(question)
        session.commit()
        keyboard = another_question_keyboard()
        await update.message.reply_text("Нужный отдел поможет тебе с этим. Они уже получили ваш запрос и напишут вам в ближайшее время🙌🏼")
        await update.message.reply_text("Есть ли у вас еще вопросы?", reply_markup=InlineKeyboardMarkup(keyboard))
        return ANSWER
    
    keyboard = topic_choice_keyboard(topics)
    await update.message.reply_text(f"Уточните к какой теме относится ваш вопрос:", reply_markup=InlineKeyboardMarkup(keyboard))

    return CLARIFICATION


async def clarification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    stmt = select(User).where(User.tg_id==int(update.effective_user.id))
    author = session.execute(stmt).scalars().first()
    if not author:
        logger.info('error/ author is not find')
        await query.edit_message_text(text="Произошел сбой в программе. Сообщите администратору")
        return ConversationHandler.END

    data = query.data.split('_')
    topic_id = data[1]
    stmt = select(Topic).where(Topic.id==int(topic_id))
    topic = session.execute(stmt).scalars().first()
    # TODO: если топик особый (требуется другой ответ типа ссылки и тд) то добавить этот функционал
    tashkent_user_id = data[2]
    kyiv_user_id = data[3]
    topic_name = data[4]
    if author.city == 'Tashkent':
        stmt = select(User).where(User.id==int(tashkent_user_id))
    else:
        stmt = select(User).where(User.id==int(kyiv_user_id))

    manager = session.execute(stmt).scalars().first()
    if not manager:
        logger.info('error/ manager is not find')
        if author.city == 'Tashkent':
            stmt = select(User).where(User.tg_id==int(default_manager_tashkent))
        else:
            stmt = select(User).where(User.tg_id==int(default_manager_kyiv))

        manager = session.execute(stmt).scalars().first()
        chat_id = manager.chat_id
        text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
               f"{analyze.question}"
        await context.bot.send_message(chat_id=chat_id, text=text)
    elif manager and not manager.chat_id:
        logger.info('error/ manager chat_id is not find')
        await query.edit_message_text(text="Произошла ошибка, обратитесь к администратору")
        return ConversationHandler.END
    
    if topic_name == 'Каналы':
        context.chat_data['manager_chat_id'] = manager.chat_id
        context.chat_data['author_name'] = author.name
        context.chat_data['author_tg_id'] = author.tg_id
        context.chat_data['author_id'] = author.id
        context.chat_data['topic_id'] = topic_id
        stmt = select(Channel)
        channels = session.execute(stmt).scalars().all()
        channel_values = [{'id': channel.id, 'name': channel.name} for channel in channels]
        keyboard = channel_choice_keyboard(channel_values)
        await query.edit_message_text(text=f"Уточните в какой канал вас добавить:", reply_markup=InlineKeyboardMarkup(keyboard))
        return CHANNEL
    
    elif topic.url_answer:
        chat_id = manager.chat_id
        text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
            f"{analyze.question}\n\nСсылка на ресурс уже отправлена пользователю"
        await context.bot.send_message(chat_id=chat_id, text=text)
        question = Question(date=datetime.date.today(),
                    text=analyze.question,
                    topic_id=int(topic_id),
                    author_id=author.id,
                    )
        session.add(question)
        session.commit()
        keyboard = another_question_keyboard()
        await context.bot.send_message(chat_id=author.chat_id, text=f"Ответы по вашему вопросу уже есть по этой ссылке:\n{topic.url_answer}")
        await query.edit_message_text(text="Есть ли у вас еще вопросы?", reply_markup=InlineKeyboardMarkup(keyboard))
        return ANSWER
    
    chat_id = manager.chat_id
    text = f"Новый вопрос от {author.name}({author.tg_id})\n\n" \
            f"{analyze.question}\n\n" \
            f"Тема: {topic_name}"
    await context.bot.send_message(chat_id=chat_id, text=text)
    question = Question(date=datetime.date.today(),
                        text=analyze.question,
                        topic_id=int(topic_id),
                        author_id=author.id,
                        )
    session.add(question)
    session.commit()

    keyboard = another_question_keyboard()
    text = "Нужный отдел поможет тебе с этим. Они уже получили ваш запрос и напишут вам в ближайшее время🙌🏼\n\nЕсть ли у вас еще вопросы?"
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ANSWER


async def channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    data = query.data.split('_')
    channel_name = data[2]
    if 'manager_chat_id' in context.chat_data:
        chat_id = context.chat_data['manager_chat_id']
    else:
        logger.error('manager not found at CHANNEL state')
        return ConversationHandler.END
    
    if 'author_name' in context.chat_data:
        author_name = context.chat_data['author_name']
    else:
        logger.error('author_name not found at CHANNEL state')
        return ConversationHandler.END
    
    if 'author_tg_id' in context.chat_data:
        author_tg_id = context.chat_data['author_tg_id']
    else:
        logger.error('author_tg_id not found at CHANNEL state')
        return ConversationHandler.END
    
    if 'author_id' in context.chat_data:
        author_id = context.chat_data['author_id']
    else:
        logger.error('author_tg_id not found at CHANNEL state')
        return ConversationHandler.END
    
    if 'topic_id' in context.chat_data:
        topic_id = context.chat_data['topic_id']
    else:
        logger.error('author_tg_id not found at CHANNEL state')
        return ConversationHandler.END

    text = f"Новый вопрос от {author_name}({author_tg_id})\n" \
           f"Канал: {channel_name}\n\n" \
           f"{analyze.question}\n\n" \
            f"Тема: добавить в канал"
    await context.bot.send_message(chat_id=chat_id, text=text)
    
    question = Question(date=datetime.date.today(),
                        text=analyze.question,
                        topic_id=int(topic_id),
                        author_id=author_id,
                        )
    session.add(question)
    session.commit()

    keyboard = another_question_keyboard()
    text = "Нужный отдел поможет тебе с этим. Они уже получили ваш запрос и напишут вам в ближайшее время🙌🏼\n\nЕсть ли у вас еще вопросы?"
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    return ANSWER


async def another_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    await query.edit_message_text(text="Задайте мне свой вопрос")
    return QUESTION


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    await query.edit_message_text(
        text="Обращайтесь, если будут другие вопросы. Хорошего дня! \n\n🤔 Задать вопрос: /question \n🗣 Оставить отзыв: /feedback"
    )

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
        "Обращайтесь, если будут другие вопросы. Хорошего дня! \n\n🤔 Задать вопрос: /question \n🗣 Оставить отзыв: /feedback"
    )

    return ConversationHandler.END


question_handler = ConversationHandler(
        entry_points=[CommandHandler('question', start)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question)],
            CLARIFICATION: [
                CallbackQueryHandler(clarification, pattern='^clarification_'),
                CallbackQueryHandler(conv_cancel, pattern='^cancel$'),
            ],
            CHANNEL: [
                CallbackQueryHandler(channel, pattern='^channel_'),
                CallbackQueryHandler(conv_cancel, pattern='^cancel$'),
            ],
            ANSWER: [
                CallbackQueryHandler(another_question, pattern='^another_question_yes$'),
                CallbackQueryHandler(finish, pattern='^another_question_no$'),
                CallbackQueryHandler(conv_cancel, pattern='^cancel$'),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
