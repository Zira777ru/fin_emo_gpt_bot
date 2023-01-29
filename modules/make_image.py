import io
from PIL import Image, ImageDraw, ImageFont
from modules.db import cursor, base
import requests


def create_portfolio_image(user_id):
    cursor.execute('SELECT symbol, buy_price, amount FROM portfolio WHERE user_id = ?', (user_id,))
    portfolio = cursor.fetchall()
    # Create an empty image with a white background
    img = Image.new('RGB', (300, (100 + len(portfolio) * 50)), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Add a title to the image
    title_font = ImageFont.truetype("arial.ttf", 20)
    draw.text((10, 10), "Portfolio", font=title_font, fill=(0, 0, 0))
        
    # Add table headers.
    header_font = ImageFont.truetype("arial.ttf", 14)
    draw.text((20, 40), "Currency", font=header_font, fill=(0, 0, 0))
    draw.text((95, 40), "Price", font=header_font, fill=(0, 0, 0))
    draw.text((160, 40), "Holdings", font=header_font, fill=(0, 0, 0))
    draw.text((220, 40), "Profit/Lose", font=header_font, fill=(0, 0, 0))

    # Add a table border to the image
    # draw.rectangle([(10, 40), (280, 100 + len(portfolio) * 50)], outline=(0, 0, 0))

    # Add the portfolio data to the image
    text_font = ImageFont.truetype("arial.ttf", 14)
    small_text_font = ImageFont.truetype("arial.ttf", 11)
    big_text_font = ImageFont.truetype("arial.ttf", 16)
    total_value = 0
    for i, holding in enumerate(portfolio):
        symbol, buy_price, amount = holding
        cursor.execute("SELECT current_price, image FROM coins WHERE symbol=?", (symbol.lower(),))
        data = cursor.fetchone()
        current_price = data[0]
        profit = (current_price - buy_price) * amount
        holdings = amount * current_price
        # print(data[1])
        response = requests.get(data[1], stream=True)
        logo = Image.open(io.BytesIO(response.content))
        logo = logo.resize((20, 20), Image.ANTIALIAS)
        # logo = logo.convert("1")
        img.paste(logo, (20, 65 + i * 30))
        # draw.bitmap((20, 65 + i * 30), logo, fill=(0, 0, 0))
        draw.text((40, 65 + i * 30), f"{symbol.upper()}", font=text_font, fill=(0, 0, 0))
        draw.text((95, 65 + i * 30), f"{round(current_price, 2)}", font=text_font, fill=(0, 0, 0))
        draw.text((160, 60 + i * 30), f"{round(holdings, 2)}", font=small_text_font, fill=(0, 0, 0))
        draw.text((160, 70 + i * 30), f"{round(amount, 2)}{symbol.upper()}", font=small_text_font, fill=(0, 0, 0))
        draw.text((220, 65 + i * 30), f"{round(profit, 2)}", font=text_font, fill=(0, 0, 0))
        # draw.rectangle([(10, 50 + i * 30), (490, 80 + i * 30)], outline=(0, 0, 0))
        total_value += holdings
    draw.text((40, 65 + len(portfolio) * 30), f"Total: {round(total_value, 2)}$", font=big_text_font, fill=(0, 0, 0))
    total_value_rub = total_value * 65
    draw.text((40, 95 + len(portfolio) * 30), f"Total: {round(total_value_rub, 2)}Rub", font=big_text_font, fill=(0, 0, 0))
    # Save the image to a file-like object
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return img_buffer


def delete_portfolio(user_id):
    cursor.execute('DELETE FROM portfolio WHERE user_id = ?', (user_id,))
    base.commit