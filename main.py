from config import *
from validators import *
from logger_debug import *
from csv_functions import *
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, Update, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from admin_functions import *
from timer import *

MODE, AMOUNT, PHONE, DONE, TO_DO = range(5)

reply_keyboard_mode = [
    ["Поделиться"],["Попросить"],["Узнать больше о боте"],["Узнать о текущей программе"]
]
markup_mode = ReplyKeyboardMarkup(reply_keyboard_mode, one_time_keyboard=True)


reply_keyboard_confirmation = [
            ["Верно"], ["Ввести данные заново"]
        ]
markup_confirmation = ReplyKeyboardMarkup(reply_keyboard_confirmation, one_time_keyboard=True)

@debug_request
def facts_to_str(user_data: Dict[str, str]) -> str:
    if user_data["Поделиться или попросить"] == "Поделиться":
        facts = f'У вас есть лишние {user_data["Количество стикеров"]} {padezh(int(user_data["Количество стикеров"]))}'
    if user_data["Поделиться или попросить"] == "Попросить":
        facts = f'Вам не хватает {user_data["Количество стикеров"]} {padezh(int(user_data["Количество стикеров"]))} на номер {user_data["Телефон"]}'
    return facts.join(["\n", "\n"])


@debug_request
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    try:
        user_id = update.message.chat.id
        await update.message.reply_text(
            'Привет! Это бот по обмену стикерами Альфа Меги! Здесь можно попросить у пользователей альфамегастикеры и поделиться ненужными стикерами с другими.',
            reply_markup=markup_mode,
        )
    except:
        logger.info('no update messase')
        try:
            user_id = update.callback_query.from_user.id
            await context.bot.send_message(
                chat_id=int(user_id),
                text='Привет! Это бот по обмену стикерами Альфа Меги! Здесь можно попросить у пользователей альфамегастикеры и поделиться ненужными стикерами с другими.',
                reply_markup=markup_mode,
            )
        except:
            logger.info('FATAL!!!!!! no userid')
    add_user_id(user_id, ALL_USERS_IDS_FILE, USERS_RATING_FILE)
    return MODE

@debug_request
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    user_id = update.message.chat.id
    add_user_id(user_id, ALL_USERS_IDS_FILE, USERS_RATING_FILE)
    await update.message.reply_text(
        '''Этот бот создан для обмена стикерами Альфа Меги 
Если вам не хватает стикеров, вы можете попросить у других пользователей. 
Если у вас есть лишние стикеры вы можете поделиться ими. 
Когда вы делитесь, ваш рейтинг увеличивается, и вы будете в приоритете, когда вам будет не хватать стикеров.

Если вы хотите оставить обратную связь или вам нужна помощь напишите нам - @stickerbothelp
        ''',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Воспользоваться ботом", callback_data="Воспользоваться ботом")]]),
        disable_web_page_preview=True
    )


@debug_request
async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    context.user_data["Поделиться или попросить"] = text
    await update.message.reply_text(f"Введите количество стикеров?")

    return AMOUNT

@debug_request
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    amount = validate_amount(text, context.user_data["Поделиться или попросить"])
    logger.info('amount validation: %s', amount)
    if amount[0] != 'true':
        await update.message.reply_text(amount[0])
        return AMOUNT
    if amount[0] == 'true':
        context.user_data["Количество стикеров"] = amount[1]
        logger.info('user_data: %s', context.user_data)
        if context.user_data["Поделиться или попросить"] == "Попросить":
            await update.message.reply_text(f"Введите ваш номер телефона?")
            return PHONE
        if context.user_data["Поделиться или попросить"] == "Поделиться":
            user_data = context.user_data
            await update.message.reply_text(
                "Итак:"
                f"{facts_to_str(user_data)}Верно?",
                reply_markup=markup_confirmation,
            )
            return DONE


@debug_request
async def received_information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    phone = validate_phone(text)
    logger.info('phone validation: %s', phone)
    if phone[0] != 'true':
        await update.message.reply_text(phone[0])
        return PHONE
    if phone[0] == 'true':
        context.user_data["Телефон"] = phone[1]
        logger.info('user_data: %s', context.user_data)

    await update.message.reply_text(
        "Итак:"
        f"{facts_to_str(user_data)}Верно?",
        reply_markup=markup_confirmation,
    )

    return DONE



@debug_request
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if user_data["Поделиться или попросить"] == "Попросить":
        await update.message.reply_text(
            f"Отлично, мы записали ваш запрос. Когда у кого-то из пользователей появятся лишние стикеры, бот отправит их вам. Когда в следующий раз вы захотите воспользоваться ботом введите команду /start",
            reply_markup=ReplyKeyboardRemove(),
        )
    if user_data["Поделиться или попросить"] == "Поделиться":
        await update.message.reply_text(
            f"Спасибо что готовы поделиться! Отправьте пожалуйста ваши лишние стикеры на номер {ADMIN_PHONE}. Когда в следующий раз вы захотите воспользоваться ботом введите команду /start",
            reply_markup=ReplyKeyboardRemove(),
        )
    add_request(update.message.chat.id, REQUESTS_FILE, user_data)
    user_data.clear()
    return ConversationHandler.END


async def information(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    must_delete = await update.message.reply_text(
        'Загружаю информацию ...',
    )
    await update.message.reply_photo(
        photo=open(INFO_PHOTO_1, 'rb'),
    )
    await update.message.reply_photo(
        photo=open(INFO_PHOTO_2, 'rb'),
    )
    await update.message.reply_text(
        f'''Программа заканчивается {DATE_FINISH_PROGRAMM.strftime("%d %b %Y")} 
Больше информации - https://www.alphamega.com.cy/en/benefits/stick-win''',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Воспользоваться ботом", callback_data="Воспользоваться ботом")]])
    )
    await context.bot.deleteMessage(message_id=must_delete.message_id, chat_id=update.message.chat_id)


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TG_TOKEN).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      MessageHandler(filters.Regex("^Воспользоваться ботом$"), start),
                      CallbackQueryHandler(start, pattern="^Воспользоваться ботом$")],
        states={
            MODE: [
                MessageHandler(filters.Regex("^(Поделиться|Попросить)$"), amount)
            ],
            AMOUNT: [
                MessageHandler(
                    filters.ALL, phone
                ),
            ],
            PHONE: [
                MessageHandler(
                    filters.ALL, received_information
                ),
            ],
            DONE: [
                MessageHandler(filters.Regex("^Ввести данные заново$"), start),
                MessageHandler(filters.TEXT, done),
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Верно$"), done),
                   MessageHandler(filters.Regex("^Ввести данные заново$"), start),
                   MessageHandler(filters.Regex("^/start"), start),
                   MessageHandler(filters.Regex("^Воспользоваться ботом$"), start),
                   CallbackQueryHandler(start, pattern="^Воспользоваться ботом$")],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('to_do', to_do_list_for_admin))
    application.add_handler(CommandHandler('notify', notify_all_users_admin))
    application.add_handler(CallbackQueryHandler(change_requests_admin, pattern="^admin transfered$"))
    application.add_handler(CommandHandler("set_reminder", set_reminder_for_admin))
    application.add_handler(CommandHandler("set_reminder_pe", set_reminder_for_programm_end))
    application.add_handler(CommandHandler('info', information))
    application.add_handler(MessageHandler(filters.Regex("^Узнать о текущей программе$"), information))
    application.add_handler(MessageHandler(filters.Regex("^Воспользоваться ботом$"), start))
    application.add_handler(CommandHandler('about', about))
    application.add_handler(MessageHandler(filters.Regex("^Узнать больше о боте$"), about))
    application.add_handler(CallbackQueryHandler(start, pattern="^Воспользоваться ботом$"))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()