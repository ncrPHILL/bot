from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = '7598024378:AAEgqjxKFrgw1tLYUzs1EQKUC8HDr9Zu8Zc'
ADMIN_CHAT_ID = 6081258504

questionnaires = {
    'ВП': """1. Как к вам обращаться? (имя или ник)
2. Какие местоимения вы используете?
3. Какой у вас эмодзи? (премиум приветствуются)
4. Предпочитаете общение на "ты" или на "вы"?
5. Есть ли у вас опыт продвижения каналов, взаимопиара и рекламы? Опишите кратко.
6. Как вы оцениваете свои навыки коммуникации?
7. Сколько времени вы знакомы с Регретеватором?
8. Насколько вы конфликтны в общении?
9. Стоит ли учитывать особые формы обращения (тон-теги, феминитивы, нейтральные выражения и т.п.)?""",
    'Хелпер': """1. Как к вам обращаться? (имя или ник)
2. Какие местоимения вы используете?
3. Какой у вас эмодзи? (премиум приветствуются)
4. Предпочитаете общение на "ты" или на "вы"?
5. Есть ли у вас опыт составления гайдов, участия в ивентах, сбора информации и т.п.? Если да, опишите кратко.
6. Сколько времени вы знакомы с Регретеватором?
7. Насколько вы конфликтны в общении?
8. Стоит ли учитывать особые формы обращения (тон-теги, феминитивы, нейтральные выражения и т.п.)?""",
    'Переводчик': """1. Как к вам обращаться? (имя или ник)
2. Какие местоимения вы используете?
3. Какой у вас эмодзи? (премиум приветствуются)
4. Предпочитаете общение на "ты" или на "вы"?
5. Сколько времени вы занимаетесь переводами?
6. Как бы вы оценили свой уровень английского? (можно указать по шкале A1–C2 или описательно)
7. Сколько времени вы знакомы с Регретеватором?
8. Насколько вы конфликтны в общении?
9. Стоит ли учитывать особые формы обращения (тон-теги, феминитивы, нейтральные выражения и т.п.)?""",
    'Редактор': """1. Как к вам обращаться? (имя или ник)
2. Какие местоимения вы используете?
3. Какой у вас эмодзи? (премиум приветствуются)
4. Предпочитаете общение на "ты" или на "вы"?
5. Имеете ли опыт в редактуре текстов? Как давно этим занимаетесь?
6. Знаете ли вы английский? Если да, какой у вас уровень?
7. Сколько времени вы знакомы с Регретеватором?
8. Насколько вы конфликтны в общении?
9. Стоит ли учитывать особые формы обращения (тон-теги, феминитивы, нейтральные выражения и т.п.)?""",
    'Смешанное': "Укажите, какие должности вы хотели бы занять, и дождитесь уникальной анкеты."
}

user_roles = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ВП", callback_data='ВП')],
        [InlineKeyboardButton("Хелпер", callback_data='Хелпер')],
        [InlineKeyboardButton("Переводчик", callback_data='Переводчик')],
        [InlineKeyboardButton("Редактор", callback_data='Редактор')],
        [InlineKeyboardButton("Смешанное", callback_data='Смешанное')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("На какую должность вы претендуете?", reply_markup=reply_markup)

# кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    role = query.data
    user_id = query.from_user.id
    user_roles[user_id] = role
    questionnaire = questionnaires.get(role, "Анкета не найдена.")
    await query.message.reply_text(questionnaire, reply_markup=ForceReply())

# анкеты
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    role = user_roles.get(user_id, "Неизвестно")
    user_name = update.message.from_user.full_name
    user_response = update.message.text

    if role == "Смешанное":
        report = f"📥 Анкета «Смешанное» от {user_name} (@{update.message.from_user.username}):\n\n" \
                 f"🧩 Желанные роли:\n{user_response}"
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=report)
    else:
        report = f"📥 Новая анкета от {user_name} (@{update.message.from_user.username}):\n\n" \
                 f"🧩 Должность: {role}\n" \
                 f"📝 Ответы:\n{user_response}"

        keyboard = [
            [
                InlineKeyboardButton("✅ Принять", callback_data=f"accept_{user_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=report, reply_markup=reply_markup)

    await update.message.reply_text("Ожидайте ответа. Если ответ задерживается на 24 часа, просто отправьте анкету заново.")

# для админа — возможность ответить вручную через reply
async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        original_text = update.message.reply_to_message.text
        lines = original_text.split('\n')
        for line in lines:
            if line.startswith("📥 Анкета «Смешанное» от") or line.startswith("📥 Новая анкета от"):
                username = line.split('@')[-1].rstrip('):')
                try:
                    await context.bot.send_message(chat_id=f"@{username}", text=update.message.text)
                    await update.message.reply_text("✅ Ответ отправлен пользователю.")
                except Exception as e:
                    await update.message.reply_text(f"❌ Не удалось отправить сообщение: {e}")
                break

# новые кнопки — принятие/отклонение
async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, user_id_str = data.split('_')
    user_id = int(user_id_str)

    try:
        if action == "accept":
            await context.bot.send_message(chat_id=user_id, text="Ваша анкета принята. Вам скоро напишут.")
        elif action == "reject":
            await context.bot.send_message(chat_id=user_id, text="К сожалению, ваша анкета отклонена.")

        original_text = query.message.text
        if "✅ Ответ отправлен пользователю." not in original_text:
            updated_text = original_text + "\n\n✅ Ответ отправлен пользователю."
            await query.edit_message_text(updated_text, reply_markup=query.message.reply_markup)

    except Exception as e:
        await query.message.reply_text(f"Ошибка при отправке: {e}")

# запуск
if __name__ == '__main__':
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler, pattern="^(ВП|Хелпер|Переводчик|Редактор|Смешанное)$"))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
        app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, admin_reply_handler))
        app.add_handler(CallbackQueryHandler(admin_button_handler, pattern=r"^(accept|reject)_\d+$"))

        print("Бот успешно запущен! Ожидаем пользователей...")
        app.run_polling()

    except Exception as e:
        print(f"Произошла ошибка при запуске бота: {e}")
