import time
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# ==================================================
# ТОКЕН
# ==================================================
TOKEN = os.getenv("TOKEN", "8958572964:AAHUMZUt1l3tSdXnZTjweHL4z8LxUPGzWsM")
bot = telebot.TeleBot(TOKEN)

# ==================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ГРУППОВОГО РЕЖИМА
# ==================================================

def is_group(chat):
    """Возвращает True, если сообщение из группового чата."""
    return chat.type in ('group', 'supergroup')


def try_dm(user_id, text, markup=None):
    """
    Пытается отправить личное сообщение пользователю.
    Возвращает True при успехе, False если пользователь не запустил бота в личке.
    """
    try:
        bot.send_message(user_id, text, reply_markup=markup)
        return True
    except telebot.apihelper.ApiTelegramException:
        return False


def try_dm_photo(user_id, path):
    """Пытается отправить фото в личные сообщения."""
    try:
        with open(path, "rb") as photo:
            bot.send_photo(user_id, photo)
    except (telebot.apihelper.ApiTelegramException, FileNotFoundError):
        pass


def prompt_to_start_private(chat_id, user):
    """Отправляет в группу тихое сообщение с просьбой запустить бота в личке."""
    me = bot.get_me()
    name = f"@{user.username}" if user.username else user.first_name
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(
        "💬 Открыть в личных сообщениях",
        url=f"https://t.me/{me.username}?start=menu"
    ))
    bot.send_message(
        chat_id,
        f"{name}, сначала запустите бота в личных сообщениях 👆",
        reply_markup=markup,
        disable_notification=True
    )

# ==================================================
# ФОТО-ВЛОЖЕНИЯ  (cat_idx, q_idx) → путь к файлу
# ==================================================
PHOTO_ATTACHMENTS = {
    (0, 2): "attached_assets/К_вопросу_о_комиссии_1785317938120.jpg",
    (1, 4): "attached_assets/К_вопросу_AID_SID_1785317930449.jpg",
}

# ==================================================
# БАЗА ЗНАНИЙ — 4 категории
# ==================================================
CATEGORIES = [
    {
        "title": "📊 Аффилет платформа AP",
        "questions": [
            (
                "Как зарегистрироваться на AP платформе?",
                "Регистрация здесь: https://ru.trip.com/partners/index?locale=ru_ru\n\nПосле регистрации получите AID 👍"
            ),
            (
                "Как получить комиссию?",
                "Пожалуйста, ознакомьтесь с информацией с официального сайта 🖥️\nhttps://www.trip.com/partners/faq/commission"
            ),
            (
                "Какой процент комиссии получает автор?",
                "💳 Комиссия зависит от типа продукта. Подробную таблицу комиссий вы можете найти в AP платформе после регистрации."
            ),
            (
                "Сколько ждать начисления комиссии после использования промокода?",
                "Период зачисления комиссии зависит от того, где оформили заказ:\n🌐 На сайте — 30 дней\n📱 В приложении — 7 дней 💸"
            ),
            (
                "Можно ли вывести деньги на российскую карту?",
                "💳 На данный момент поддерживаются только USD и HKD."
            ),
            (
                "Когда будут поддерживать российские карты?",
                "💳 Российские карты пока не поддерживаются, но мы активно работаем над этим и в будущем добавим поддержку."
            ),
            (
                "Какой минимальный вывод?",
                "Минимум для вывода: 200 USD 💰\nЕсли меньше — переносится на следующий период 👍"
            ),
            (
                "Когда мне придят деньги?",
                "Расчетный период: 40–60 рабочих дней 📅\nКаждые 30 дней проверяется баланс. Если > 200 USD — можно выводить ✅"
            ),
        ]
    },
    {
        "title": "🎟️ Всё о промокодах блогера",
        "questions": [
            (
                "Что такое промокод блогера?",
                "🎟️ Промокод блогера — это ваш персональный код для заработка. Когда пользователи вводят его в поиске Trip App, они попадают на вашу личную страницу со скидками и рекомендациями. Все заказы, оформленные в течение 7 дней (через приложение) или 30 дней (через сайт), засчитываются вам."
            ),
            (
                "Как использовать промокод блогера?",
                "Промокод блогера — это ваш личный код для заработка. Пользователь вводит его в поиске Trip.com → попадает на вашу страницу → все заказы за 7–30 дней идут вам.\n\nКак использовать:\n1️⃣ Получите свой промокод блогера\n2️⃣ Разместите в bio/описании/закрепленном комментарии\n3️⃣ Озвучьте в видео 🎉"
            ),
            (
                "Промокод блогера работает только для новых пользователей?",
                "Промокод блогера работает для всех пользователей — как новых, так и существующих ✅"
            ),
            (
                "Как получить промокод блогера?",
                "Шаг 1. Зарегистрируйтесь на партнёрской платформе Trip.com:\n🔗 https://ru.trip.com/partners/index?locale=ru_ru\n\nШаг 2. Получите ваш AID (идентификатор аккаунта) и SID (идентификатор сайта) в личном кабинете после регистрации.\n\nШаг 3. Заполните форму для получения промокода блогера:\n📋 https://trip.larkenterprise.com/share/base/form/shrcnA93dUWGnhu28OkmMsQGCIh"
            ),
            (
                "Что такое SID и AID? Где их найти?",
                "AID = номер аккаунта\nSID = номер сайта\n\nГде найти:\nAP платформа → Account → Manage My Sites\nТам увидите оба номера 👍"
            ),
            (
                "Как узнать статус заявки на промокод блогера?",
                "Шаг 1. После подачи заявки админы лично уведомят вас, когда промокод блогера будет готов.\n⏳ Обычно это занимает 3–5 рабочих дней.\n\nШаг 2. Проверьте, активен ли ваш промокод блогера:\n📱 Откройте приложение Trip.com → переключитесь на RU‑регион → выполните поиск по своему промокоду."
            ),
            (
                "Какие скидки получат пользователи?",
                "Купоны — это скидки для пользователей, которые вводят ваш промокод блогера.\n\n💳 Типы купонов:\n🆕 Купон для новых пользователей\n🔒 Фиксированные промо-купоны\n\nВсе купоны отображаются на вашей личной странице, когда пользователь вводит промокод блогера.\n\n🏆 Планы на будущее: мы будем выдавать дополнительные купоны блогерам с хорошими продажами. Количество ограничено ⚠️"
            ),
            (
                "Где размещать промокод блогера?",
                "📸 Instagram (ссылки запрещены ❌):\n• 📝 В разделе bio\n• 📄 В описании поста\n• 📌 Закрепите в первом комментарии\n• 🎤 Озвучьте в видео\n\n💬 Telegram:\n• 🔗 Разместите ссылку в канале\n• ℹ️ Добавьте в описание канала\n\n🎥 YouTube / TikTok:\n• 📝 Добавьте в описание видео\n• 📌 Закрепите в первом комментарии"
            ),
        ]
    },
    {
        "title": "🤝 Реферальная программа",
        "questions": [
            (
                "Какой приветственный бонус (coins)?",
                "Приветственный бонус: 2900 coins 🎁\n\nУсловия получения:\n📝 Опубликуйте 5 рекомендованных постов\n👥 Достигните 5000 подписчиков\n\nПосле выполнения — начисляется автоматически ✅"
            ),
            (
                "Когда придят приветственные coins?",
                "Бонус начисляется автоматически после выполнения условий (5 постов + 5000 подписчиков).\n\nЕсли условия выполнены, но бонус не пришёл — напишите админам (@iamlisha2510 @zhengcao01), разберёмся! 🔍"
            ),
            (
                "Пригласил(а) друга, но бонус не получил(а)?",
                "Обычно это значит, что приглашённый не прошёл верификацию.\n\nПожалуйста, напишите нашим админам (@iamlisha2510 @zhengcao01) ваш Trip nickname — они проверят статус 🔍"
            ),
        ]
    },
    {
        "title": "🔄 Бартер и коллаборации",
        "questions": [
            (
                "Какие сейчас есть бартерные проекты?",
                "🇨🇳 GO China\n\n"
                "🏨 Отели\n"
                "📝 https://trip.larkenterprise.com/share/base/form/shrcnJRSAC7DZfkSxyRk1rIr76c\n"
                "💡 https://drive.google.com/file/d/1yOgRjLd2y2YqeadFRwKTQvUDDJ-hr8Wz/view?usp=sharing\n\n"
                "🎟️ Достопримечательности (без Диснея и Lego)\n"
                "📝 https://trip.larkenterprise.com/share/base/form/shrcnQuaPmnU1YEmlQlahlgDRZc\n"
                "💡 https://drive.google.com/file/d/12PjPhDn1eNfNoVaumQvyRKRdCf6YYYS9/view?usp=sharing\n\n"
                "🍜 Taste of China\n"
                "📝 https://trip.larkenterprise.com/share/base/form/shrcnDHL1HR6ujXS2Fn1vn4MiWf\n"
                "💡 https://drive.google.com/file/d/1bjoNUFz6aPs5mDJPQ4GcfMuMh2y1vbwP/view?usp=sharing\n\n"
                "─────────────────────\n"
                "🇻🇳 GO Vietnam\n\n"
                "🏨 Отели\n"
                "📝 https://trip.larkenterprise.com/share/base/form/shrcnvdWkA1LEaiq2CF1Jf1vvZe\n"
                "💡 https://drive.google.com/file/d/19HK9gA-fOMdCDHQ-Gw2jrrZOgG2N0DFr/view?usp=sharing\n\n"
                "🎟️ Достопримечательности\n"
                "📝 https://trip.larkenterprise.com/share/base/form/shrcngmU3t8o9HdrSi8TghulHTo\n"
                "💡 https://drive.google.com/file/d/1ZpP5K9M2JYpuoXR1-FqdYN3w99jx4XO-/view?usp=sharing\n\n"
                "─────────────────────\n"
                "🇯🇵 GO Japan\n\n"
                "🎟️ Достопримечательности\n"
                "📝 https://trip.larkenterprise.com/share/base/form/shrcnnCvHrpCvMxb4ywHLLUfobb\n"
                "💡 https://drive.google.com/file/d/1X1RKyrVTrGDukmgMi_kVX2shQyM_K3eU/view?usp=sharing\n\n"
                "⚠️ Обязательно оставьте заявку по ссылке минимум за 2 недели до путешествия!"
            ),
            (
                "Когда можно узнать, прошла ли заявка?",
                "Обычно ответ приходит за 2 недели до начала поездки.\n\nНапишите админам (@iamlisha2510 @zhengcao01) — они уточнят у организаторов."
            ),
            (
                "Какие требования к участию в бартерном проекте?",
                "Рекомендуем подать заявку на личный промокод блогера — так вы сможете получать комиссию.\n\nШаги:\n1️⃣ Зарегистрируйтесь на партнёрской платформе Trip.com\n2️⃣ Получите ваш AID (Account ID) и SID (Site ID)\n3️⃣ Заполните форму для получения промокода блогера:\n📋 https://trip.larkenterprise.com/share/base/form/shrcnA93dUWGnhu28OkmMsQGCIh"
            ),
        ]
    },
]

# ==================================================
# СТОП-СЛОВА
# ==================================================
STOP_WORDS = {
    "а", "в", "во", "вот", "из", "и", "к", "как", "ко", "мне", "мой",
    "на", "не", "но", "о", "об", "от", "по", "при", "с", "со", "то",
    "у", "уже", "что", "это", "я", "он", "она", "они", "оно", "мы",
    "вы", "ты", "для", "до", "за", "под", "про", "без", "над", "или",
    "да", "нет", "если", "тоже", "так", "еще", "ещё", "вообще", "можно",
    "нужно", "надо", "есть", "бы", "ли", "же", "там", "тут",
    "когда", "где", "зачем", "почему", "кто", "чем", "чего",
    "меня", "его", "её", "их", "нас", "вас", "им", "нам", "вам",
}


def normalize(text):
    for ch in ['?', '!', '.', ',', '-', '«', '»', '"', "'", '—', ':', ';', '(', ')']:
        text = text.replace(ch, ' ')
    return text.lower().strip()


def get_keywords(text):
    return [w for w in normalize(text).split() if w not in STOP_WORDS and len(w) >= 3]


def score_match(user_words, faq_keywords):
    if not faq_keywords:
        return 0.0
    score = 0
    for kw in faq_keywords:
        if kw in user_words:
            score += 2
            continue
        for uw in user_words:
            if kw in uw or uw in kw:
                score += 1
                break
    return score / (len(faq_keywords) * 2)


# Плоский индекс для текстового поиска
SEARCH_INDEX = [
    (ci, qi, get_keywords(q))
    for ci, cat in enumerate(CATEGORIES)
    for qi, (q, _) in enumerate(cat["questions"])
]

# ==================================================
# КЛАВИАТУРЫ
# ==================================================

WELCOME_TEXT = (
    "👋 Привет! Я бот поддержки Trip Moments.\n\n"
    "📌 Выберите раздел, который вас интересует:"
)


def build_categories_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    for i, cat in enumerate(CATEGORIES):
        markup.add(InlineKeyboardButton(cat["title"], callback_data=f"cat_{i}"))
    return markup


def build_questions_keyboard(cat_idx):
    markup = InlineKeyboardMarkup(row_width=1)
    for qi, (question, _) in enumerate(CATEGORIES[cat_idx]["questions"]):
        label = question[0].upper() + question[1:]
        markup.add(InlineKeyboardButton(label, callback_data=f"faq_{cat_idx}_{qi}"))
    markup.add(InlineKeyboardButton("← Назад к разделам", callback_data="menu"))
    return markup


def build_back_to_cat_keyboard(cat_idx):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("← Назад к вопросам", callback_data=f"cat_{cat_idx}"))
    markup.add(InlineKeyboardButton("🏠 Главное меню", callback_data="menu"))
    return markup


# ==================================================
# ПЕРЕХОД С ЭФФЕКТОМ
# ==================================================

def transition(chat_id, message_id, final_text, final_markup):
    """Кнопки исчезают → искра → появляется текст."""
    bot.edit_message_text("✨", chat_id, message_id)
    time.sleep(0.4)
    bot.edit_message_text(final_text, chat_id, message_id, reply_markup=final_markup)


def send_photo_if_needed(chat_id, cat_idx, q_idx):
    """Отправляет фото после ответа, если оно есть для данного вопроса."""
    path = PHOTO_ATTACHMENTS.get((cat_idx, q_idx))
    if path:
        with open(path, "rb") as photo:
            bot.send_photo(chat_id, photo)


# ==================================================
# КОМАНДЫ
# ==================================================

@bot.message_handler(commands=['start', 'menu'])
def send_start(message):
    if is_group(message.chat):
        # В группе: отправляем тихое сообщение с кнопкой "открыть в личке"
        me = bot.get_me()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            "💬 Открыть в личных сообщениях",
            url=f"https://t.me/{me.username}?start=menu"
        ))
        bot.send_message(
            message.chat.id,
            "👋 Нажмите кнопку ниже — я отвечу вам в личных сообщениях, чтобы никто не видел ваш вопрос.",
            reply_markup=markup,
            disable_notification=True
        )
    else:
        bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=build_categories_keyboard())


# ==================================================
# ОБРАБОТЧИКИ КНОПОК
# ==================================================

@bot.callback_query_handler(func=lambda call: call.data == "menu")
def handle_menu(call):
    if is_group(call.message.chat):
        sent = try_dm(call.from_user.id, WELCOME_TEXT, build_categories_keyboard())
        if sent:
            bot.answer_callback_query(call.id, text="✉️ Отправлено в личные сообщения", show_alert=False)
        else:
            bot.answer_callback_query(call.id, text="⚠️ Сначала запустите бота в личке!", show_alert=True)
            prompt_to_start_private(call.message.chat.id, call.from_user)
    else:
        bot.answer_callback_query(call.id, text="🏠")
        transition(call.message.chat.id, call.message.message_id,
                   WELCOME_TEXT, build_categories_keyboard())


@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def handle_category(call):
    cat_idx = int(call.data.split("_")[1])
    cat = CATEGORIES[cat_idx]
    if is_group(call.message.chat):
        text = f"{cat['title']}\n\nВыберите вопрос:"
        sent = try_dm(call.from_user.id, text, build_questions_keyboard(cat_idx))
        if sent:
            bot.answer_callback_query(call.id, text="✉️ Отправлено в личные сообщения", show_alert=False)
        else:
            bot.answer_callback_query(call.id, text="⚠️ Сначала запустите бота в личке!", show_alert=True)
            prompt_to_start_private(call.message.chat.id, call.from_user)
    else:
        bot.answer_callback_query(call.id, text="✨")
        transition(
            call.message.chat.id, call.message.message_id,
            f"{cat['title']}\n\nВыберите вопрос:",
            build_questions_keyboard(cat_idx)
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_"))
def handle_faq_button(call):
    _, cat_str, q_str = call.data.split("_")
    cat_idx, q_idx = int(cat_str), int(q_str)
    question, answer = CATEGORIES[cat_idx]["questions"][q_idx]
    header = question[0].upper() + question[1:]
    if is_group(call.message.chat):
        sent = try_dm(call.from_user.id, f"❓ {header}\n\n{answer}", build_back_to_cat_keyboard(cat_idx))
        if sent:
            bot.answer_callback_query(call.id, text="✉️ Отправлено в личные сообщения", show_alert=False)
            # Фото тоже в личку
            path = PHOTO_ATTACHMENTS.get((cat_idx, q_idx))
            if path:
                try_dm_photo(call.from_user.id, path)
        else:
            bot.answer_callback_query(call.id, text="⚠️ Сначала запустите бота в личке!", show_alert=True)
            prompt_to_start_private(call.message.chat.id, call.from_user)
    else:
        bot.answer_callback_query(call.id, text="✨")
        transition(
            call.message.chat.id, call.message.message_id,
            f"❓ {header}\n\n{answer}",
            build_back_to_cat_keyboard(cat_idx)
        )
        send_photo_if_needed(call.message.chat.id, cat_idx, q_idx)


# ==================================================
# ТЕКСТОВОЙ ПОИСК (запасной вариант)
# ==================================================

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if not message.text or message.text.startswith('/'):
        return

    user_text = normalize(message.text)
    user_words = get_keywords(message.text)

    best_score = 0.0
    best_cat = 0
    best_q_idx = 0
    best_answer = None
    best_question = None

    for ci, qi, kws in SEARCH_INDEX:
        if user_text == normalize(CATEGORIES[ci]["questions"][qi][0]):
            best_score = 1.0
            best_cat = ci
            best_q_idx = qi
            best_question, best_answer = CATEGORIES[ci]["questions"][qi]
            break
        s = score_match(user_words, kws)
        if s > best_score:
            best_score = s
            best_cat = ci
            best_q_idx = qi
            best_question, best_answer = CATEGORIES[ci]["questions"][qi]

    if is_group(message.chat):
        # В группе — всё идёт в личку
        if best_score >= 0.35:
            header = best_question[0].upper() + best_question[1:]
            sent = try_dm(message.from_user.id,
                          f"❓ {header}\n\n{best_answer}",
                          build_back_to_cat_keyboard(best_cat))
            if sent:
                path = PHOTO_ATTACHMENTS.get((best_cat, best_q_idx))
                if path:
                    try_dm_photo(message.from_user.id, path)
            else:
                prompt_to_start_private(message.chat.id, message.from_user)
        else:
            sent = try_dm(message.from_user.id,
                          "🤔 Я не совсем понял ваш вопрос.\n\nВыберите раздел из меню:",
                          build_categories_keyboard())
            if not sent:
                prompt_to_start_private(message.chat.id, message.from_user)
    else:
        # В личке — обычное поведение
        if best_score >= 0.35:
            header = best_question[0].upper() + best_question[1:]
            bot.reply_to(
                message,
                f"❓ {header}\n\n{best_answer}",
                reply_markup=build_back_to_cat_keyboard(best_cat)
            )
            send_photo_if_needed(message.chat.id, best_cat, best_q_idx)
        else:
            bot.reply_to(
                message,
                "🤔 Я не совсем понял ваш вопрос.\n\nВыберите раздел из меню:",
                reply_markup=build_categories_keyboard()
            )


# ==================================================
# ЗАПУСК
# ==================================================
print("✅ Бот Trip Moments успешно запущен!")

# Убираем устаревшие команды из меню Telegram (куб с точками)
bot.set_my_commands([
    BotCommand("start", "Открыть главное меню"),
    BotCommand("menu", "Открыть главное меню"),
])

bot.infinity_polling()
