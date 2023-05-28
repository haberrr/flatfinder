import requests

from flatfinder.settings import Settings

BASE_URL = f'https://api.telegram.org/bot{Settings.TG_BOT_TOKEN}/{{}}'


def get_updates():
    url = BASE_URL.format('getUpdates')
    response = requests.get(url)
    response.raise_for_status()

    print(response.json())


if __name__ == '__main__':
    get_updates()
