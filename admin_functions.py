from config import *
from logger_debug import *
import pandas as pd
from telegram.error import Forbidden
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from csv_functions import *

@debug_request
async def to_do_list_for_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat_id
    if chat_id == ADMIN_ID:
        real_balance = int(context.args[0])
        logger.info('real balance: %s', real_balance)
        to_do_list = make_to_do_list(real_balance)
        context.user_data['to_do'] = to_do_list
        logger.info('user_data with todo: %s', context.user_data)
        if len(to_do_list) == 0:
            reply = "nothing to transfer"
            await update.message.reply_text(f"formed balance={formed_balance()} \n {reply}")
        else:
            reply = "\n".join([f"transfer {i[0]} to phone {i[1]}" for i in to_do_list]).join(["\n", "\n"])
            keyboard_to_do = [[InlineKeyboardButton("Перевел", callback_data="admin transfered")]]
            reply_markup_to_do = InlineKeyboardMarkup(keyboard_to_do)
            await update.message.reply_text(f"formed balance={formed_balance()} \n {reply}", reply_markup=reply_markup_to_do)
    else:
        await update.message.reply_text('Неверная команда. Чтобы попросить или поделиться стикерами нажмите /start')

@debug_request
async def change_requests_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = query.from_user.id
    await query.answer()
    if chat_id == ADMIN_ID:
        change_requests(context.user_data['to_do'])
        to_do = "\n".join([f"transfered {i[0]} to phone {i[1]}" for i in context.user_data['to_do']]).join(["\n", "\n"])
        await query.edit_message_text(text=f'Файл requests.csv успешно обновлен \n {to_do}')
    else:
        await query.edit_message_text(text='Неверная команда. Чтобы попросить или поделиться стикерами нажмите /start')

@debug_request
async def notify_all_users_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat_id
    if chat_id == ADMIN_ID:
        user_id_df = pd.read_csv(ALL_USERS_IDS_FILE, index_col=0)
        for chat_id in np.unique(user_id_df.user_id):
            logger.info('trying to notify chat_id: %s', chat_id)
            try:
                await context.bot.send_message(
                    chat_id=int(chat_id),
                    text=UPDATE_TEXT_0,
                    reply_markup=ReplyKeyboardRemove()

                )
                await context.bot.send_message(
                    chat_id=int(chat_id),
                    text=UPDATE_TEXT_1,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Воспользоваться ботом", callback_data="Воспользоваться ботом")]])

                )
                logger.info('notified chat_id: %s', chat_id)
            except Forbidden:
                logger.info('Unauthorized chat_id: %s', chat_id)
            except:
                logger.info('Unknown ERROR chat_id: %s', chat_id)
    else:
        update.message.reply_text('Неверная команда')


