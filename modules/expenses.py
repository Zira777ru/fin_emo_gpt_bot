import re
from datetime import datetime, timedelta

from modules.db import cursor, base


now = datetime.now()
current_month_start = datetime(now.year, now.month, 1)
current_month_end = current_month_start + timedelta(days=31)

async def exp_add(state, user_id):
    async with state.proxy() as data:
        expense = data['expense'].split("\n")
        success = "\n<b>✅ Successfully added:</b>\n"
        failed = "\n<b>❌ Failed to add:</b>\n"
        for string in expense:
            match = re.search(r'^\d+|\d+$', string)
            if match:
                first_num = int(match.group())
                remaining_string = re.sub(r'^\d+|\d+$', "", string).lstrip()
                cursor.execute('INSERT INTO finance (user_id, description, amount) VALUES (?, ?, ?)', (user_id, remaining_string, first_num))
                success += f"{first_num} {remaining_string}\n"
            else:
                failed += f"{string}\n"
        base.commit()
        if failed != "\n<b>❌ Failed to add:</b>\n":
            failed += f"\n<b>❗️ Try again!</b>\n"
            return success + failed
        else:
            return success


def get_all_expenses(user_id):
    cursor.execute("SELECT * FROM finance WHERE user_id=? ORDER BY date DESC", (user_id,))
    all_expenses = cursor.fetchall()
    return all_expenses

def get_total_expenses(user_id):
    # Get the total amount of all expenses for the current user
    cursor.execute("SELECT SUM(amount) FROM finance WHERE user_id=?", (user_id,))
    total_expenses = cursor.fetchone()
    return total_expenses

def get_current_month_expenses(user_id):
    # Get the total amount of expenses for the current month
    cursor.execute("SELECT SUM(amount) FROM finance WHERE user_id=? AND date >= ? AND date <= ?", (user_id, current_month_start, current_month_end))
    current_month_expenses = cursor.fetchone()
    return current_month_expenses

def get_last_month_expenses(user_id):
    # Get the total amount of expenses for the last month
    last_month_start = current_month_start - timedelta(days=31)
    last_month_end = current_month_start
    cursor.execute("SELECT SUM(amount) FROM finance WHERE user_id=? AND date >= ? AND date <= ?", (user_id, last_month_start, last_month_end))
    last_month_expenses = cursor.fetchone()
    return last_month_expenses


#new
def get_expenses_today(user_id):
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    cursor.execute("SELECT amount, description FROM finance WHERE user_id=? AND date >= ? AND date <= ? ORDER BY date DESC", (user_id, today_start, today_end))
    expenses_today = cursor.fetchall()
    return expenses_today

def get_expenses_yesterday(user_id):
    yesterday_start = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday_start + timedelta(days=1)
    cursor.execute("SELECT amount, description FROM finance WHERE user_id=? AND date >= ? AND date <= ? ORDER BY date DESC", (user_id, yesterday_start, yesterday_end))
    expenses_yesterday = cursor.fetchall()
    return expenses_yesterday

def get_expenses_7_days(user_id):
    seven_days_ago = datetime.now() - timedelta(days=7)
    cursor.execute("SELECT amount, description FROM finance WHERE user_id=? AND date >= ? ORDER BY date DESC", (user_id, seven_days_ago))
    expenses_7_days = cursor.fetchall()
    return expenses_7_days

def get_current_month_expenses(user_id):
    current_month_start = datetime(now.year, now.month, 1)
    current_month_end = current_month_start + timedelta(days=31)
    cursor.execute("SELECT amount, description FROM finance WHERE user_id=? AND date >= ? AND date <= ? ORDER BY date DESC", (user_id, current_month_start, current_month_end))
    current_month_expenses = cursor.fetchall()
    return current_month_expenses

def get_last_month_expenses(user_id):
    last_month_start = (datetime(now.year, now.month, 1) - timedelta(days=31)).replace(day=1)
    last_month_end = last_month_start + timedelta(days=31)
    cursor.execute("SELECT amount, description FROM finance WHERE user_id=? AND date >= ? AND date <= ? ORDER BY date DESC", (user_id, last_month_start, last_month_end))
    last_month_expenses = cursor.fetchall()
    return last_month_expenses
