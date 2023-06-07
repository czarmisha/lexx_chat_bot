import logging
from telegram import Update, ForceReply
from telegram.ext import ContextTypes, CommandHandler

# from sqlalchemy import select
from db.models import Session, engine

local_session = Session(bind=engine)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info('!!@@'*22)
    logging.info(update)
    logging.info(update.effective_user)
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    # if not update.message.chat.type == 'private':
    #     # update.message.reply_text(f"{messages['private_error']['ru']} \n\n {messages['private_error']['uz']}")
    #     return 
    # else:
    #     statement = select(Group)
    #     group = local_session.execute(statement).scalars().first()
    #     logger.info('!!!!!!!!!!!!!', group.tg_id)
    #     author = context.bot.get_chat_member(group.tg_id, update.effective_user.id)
    #     if author.status == 'left' or author.status == 'kicked' or not author.status:
    #         context.bot.send_message(chat_id=update.effective_chat.id,
    #                                 text=f"{messages['auth_err']['ru']} / {messages['auth_err']['uz']}")
    #         return
    #     reply_keyboard = [['/reserve', '/display'], ['/my_events', '/feedback']]
    #     markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

    #     update.message.reply_text(f"{messages['start_text']['ru']} \n\n {messages['start_text']['uz']}",
    #                               reply_markup=markup_key)
    #     update.message.reply_text(f"{messages['attention']['ru']} \n\n {messages['attention']['uz']}")
    #     update.message.reply_text(f"Документация: \nhttps://telegra.ph/Dokumentaciya-k-botu-Event-Scheduler-Uzinfocom-08-18", parse_mode='HTML')


start_handler = CommandHandler('start', start)
