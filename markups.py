from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import modules.expenses as ex

MAIN = ["💲Expense", "📝Dairy", "😐Emotion", "♈️Zodiac", "💰Coins"]
EXP_MENU = ["✏️Add Expense", "📚Show Expenses"]
ZODIAC_SINGS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
EMOTIONS = ["Joy", "Interest", "Surprise", "Sadness", "Anger", "Disgust", "Contempt", "Fear", "Shame"]
SHOW_EXP = {"Show Today Exp": ex.get_expenses_today,
            "Show Yesterday": ex.get_expenses_yesterday,
            "Show 7 Days Exp": ex.get_expenses_7_days,
            "Show Current Month": ex.get_current_month_expenses,
            "Show Last Month": ex.get_last_month_expenses}
BACK = ['↩️Back']


def generate_keyboard(items, row_width=2, include_cancel_button=True):
    buttons = []
    for item in items:
        button = InlineKeyboardButton(text=item, callback_data=f'btn_{item}')
        buttons.append(button)
    if include_cancel_button:
        buttons.append(InlineKeyboardButton(text=BACK[0], callback_data=f'btn_{BACK[0]}'))
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    keyboard.add(*buttons)
    return keyboard

main_menu = generate_keyboard(MAIN, include_cancel_button=False)
expense_menu = generate_keyboard(EXP_MENU)
show_expense_menu = generate_keyboard(SHOW_EXP)
zodiac_menu = generate_keyboard(ZODIAC_SINGS)
emotion_menu = generate_keyboard(EMOTIONS)
cancel_menu = generate_keyboard(BACK, include_cancel_button=False)

