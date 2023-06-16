from telegram import InlineKeyboardButton


def topic_choice_keyboard(topics):
    return [
        *[[
            InlineKeyboardButton(f"▶️ {topic['topic']}", callback_data=f"clarification_{topic['topic_id']}_{topic['tashkent_user_id']}_{topic['kyiv_user_id']}")
        ] for topic in topics],
        [InlineKeyboardButton(f"✖️ Отмена", callback_data='cancel')],
    ]


def another_question_keyboard():
    return [
        [
            InlineKeyboardButton("Да", callback_data=f"another_question_yes"),
            InlineKeyboardButton("Нет", callback_data=f"another_question_no"),
        ],
        [InlineKeyboardButton(f"✖️ Отмена", callback_data='cancel')],
    ]


def city_keyboard():
    return [
        [
            InlineKeyboardButton("Ташкент", callback_data=f"city_Tashkent"),
            InlineKeyboardButton("Киев", callback_data=f"city_Kyiv"),
        ],
        [InlineKeyboardButton(f"✖️ Отмена", callback_data='cancel')],
    ]