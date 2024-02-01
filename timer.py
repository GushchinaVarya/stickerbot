import datetime

from logger_debug import *
from config import *
import pandas as pd
import numpy as np
from logger_debug import *
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes

@debug_request
async def reminder_for_admin(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    if (job.chat_id == ADMIN_ID):
        await context.bot.send_message(job.chat_id, text=f"Пора сделать переводы! {job.data} введите /to_do <текущий баланс>!")

@debug_request
async def set_reminder_for_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    if (chat_id == ADMIN_ID):
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(reminder_for_admin, 60, chat_id=chat_id, name=str(chat_id), data='some info')
        text = "Timer reminder for admin successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)
    else:
        await update.effective_message.reply_text("Неверная команда")


async def reminder_for_programm_end(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    user_id_df = pd.read_csv(ALL_USERS_IDS_FILE, index_col=0)
    for chat_id in np.unique(user_id_df.user_id):
        logger.info('trying to notify chat_id: %s', chat_id)
        #try:
        await context.bot.send_message(
            chat_id=int(chat_id),
            text=f'Программа заканчивается {DATE_FINISH_PROGRAMM.strftime("%d %b %Y")}. Если у вас есть лишние стикеры или вам не хватает, нажмите "Воспользоваться ботом" ',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Воспользоваться ботом", callback_data="Воспользоваться ботом")]])

        )
        logger.info('notified chat_id: %s', chat_id)
        #except:
        #    logger.info('Unknown ERROR chat_id: %s', chat_id)


async def set_reminder_for_programm_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    if (chat_id == ADMIN_ID):
        job_removed = remove_job_if_exists(str(chat_id)+'_program_end_1', context)
        context.job_queue.run_once(reminder_for_programm_end, (DATE_FINISH_PROGRAMM - datetime.timedelta(days=14)),
                                   chat_id=chat_id, name=str(chat_id)+'_program_end_1', data='some info')
        text = "Timer for programm end reminder 1 successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

        job_removed = remove_job_if_exists(str(chat_id) + '_program_end_2', context)
        context.job_queue.run_once(reminder_for_programm_end, (DATE_FINISH_PROGRAMM - datetime.timedelta(days=7)),
                                   chat_id=chat_id, name=str(chat_id) + '_program_end_2', data='some info')
        text = "Timer for programm end reminder 2 successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

        job_removed = remove_job_if_exists(str(chat_id) + '_program_end_3', context)
        context.job_queue.run_once(reminder_for_programm_end, (DATE_FINISH_PROGRAMM - datetime.timedelta(days=3)),
                                   chat_id=chat_id, name=str(chat_id) + '_program_end_3', data='some info')
        text = "Timer for programm end reminder 3 successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True