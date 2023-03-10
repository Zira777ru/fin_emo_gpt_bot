import sqlite3


base = sqlite3.connect('database.db', check_same_thread=False)
cursor = base.cursor()


def sql_start():

    if base:
        print('Data base connected OK!')
    cursor.execute('CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT, authorized INTEGER, registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    cursor.execute('CREATE TABLE IF NOT EXISTS finance(id INTEGER PRIMARY KEY, user_id INTEGER, description TEXT, amount INT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(user_id))')
    cursor.execute('CREATE TABLE IF NOT EXISTS emotion(id INTEGER PRIMARY KEY, user_id INTEGER, emotion TEXT, desc_emo TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(user_id))')
    cursor.execute('CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT, username TEXT, response_text TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(user_id))')
    cursor.execute('CREATE TABLE IF NOT EXISTS dairy(id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT, message_id TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(user_id))')
    cursor.execute('CREATE TABLE IF NOT EXISTS coins(id INTEGER PRIMARY KEY, symbol TEXT, name TEXT, current_price REAL, market_cap_rank INTEGER, image TEXT, market_cap REAL, price_change_percentage_24h REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS portfolio(id INTEGER PRIMARY KEY, user_id INTEGER, symbol TEXT, buy_price REAL, buy_date TIMESTAMP, amount REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    base.commit()