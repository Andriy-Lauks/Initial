import requests
from bs4 import BeautifulSoup
import json

URL = 'https://minfin.com.ua/currency/banks/'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'
}


def get_html(url, params=''):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('tr', class_='row--collapse')
    banks = []

    for item in items:
        banks.append(
            {
                'bank': item.find('td', class_='js-ex-rates mfcur-table-bankname').get_text(strip=True),
                'buy': item.find('td', class_='responsive-hide mfm-text-right mfm-pr0').get_text(),
                'sell': item.find('td', class_='responsive-hide mfm-text-left mfm-pl0').get_text(),
                'upd_time': item.find('td', class_='respons-collapsed mfcur-table-refreshtime').get_text()
            }
        )
    return banks


def parser(currency='usd/'):
    url = f'{URL}{currency}'
    html = get_html(url)

    if html.status_code == 200:
        output = get_content(html.text)
    else:
        print('HTML Error, status code {}!'.format(html.status_code))

    return output


if __name__ == '__main__':
    parser()
