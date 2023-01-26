import requests

from modules.db import base, cursor

def coingecko():
    # Make API call
    url = ('https://api.coingecko.com/api/v3/coins/markets?'
           + 'vs_currency=USD&order=market_cap_desc&per_page=250'
           + '&page=1&sparkline=false')
    data = requests.get(url).json()
    coins = []
    for coin in data:
        symbol = coin['symbol']
        name = coin['name']
        current_price = coin['current_price']
        market_cap_rank = coin['market_cap_rank']
        image = coin['image']
        market_cap = coin['market_cap']
        price_change_percentage_24h = coin['price_change_percentage_24h']
        # Check if coin already exists in database
        cursor.execute("SELECT COUNT(*) FROM coins WHERE symbol=?", (symbol,))
        result = cursor.fetchone()[0]
        if result == 0:
            # Insert coin into database
            cursor.execute("INSERT INTO coins (symbol, name, current_price, market_cap_rank, image, market_cap, price_change_percentage_24h) VALUES (?,?,?,?,?,?,?)", (symbol, name, current_price, market_cap_rank, image, market_cap, price_change_percentage_24h))
        else:
            # Update existing coin in database
            cursor.execute("UPDATE coins SET name=?, current_price=?, market_cap_rank=?, image=?, market_cap=?, price_change_percentage_24h=? WHERE symbol=?", (name, current_price, market_cap_rank, image, market_cap, price_change_percentage_24h, symbol))
        
        cursor.execute("SELECT * FROM coins WHERE symbol=?", (symbol,))
        coin = cursor.fetchone()
        coin_dict = {
            'symbol': coin[0],
            'name': coin[1],
            'current_price': coin[2],
            'market_cap_rank': coin[3],
            'image': coin[4],
            'market_cap': coin[5],
            'price_change_percentage_24h': coin[6],
        }
        coins.append(coin_dict)
    # Commit changes and close connection
    print('Coins Added')
    base.commit()

def get_coin_data(symbols):
    data = {}
    for symbol in symbols:
        cursor.execute("SELECT current_price, price_change_percentage_24h FROM coins WHERE symbol=?", (symbol.lower(),))
        result = cursor.fetchone()
        if result:
            data[symbol] = {"current_price": result[0], "price_change_percentage_24h": result[1]}
        else:
            data[symbol] = None
    return data



