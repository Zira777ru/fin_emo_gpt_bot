import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


user_agent = UserAgent()

def horoscope(zodiac_sign):
    headers = {"User-Agent": user_agent.random}
    res = requests.get(f'https://1001goroskop.ru/?znak={zodiac_sign}', headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    data = soup.find('div', attrs={'itemprop': 'description'})
    return data.p.text