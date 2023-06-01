import time
import logging
from typing import List
from datetime import datetime

import requests

from flatfinder.sources import NotificationBaseABC
from flatfinder.sources.base.db import db
from flatfinder.settings import Settings

BASE_URL = f'https://api.telegram.org/bot{Settings.TG_BOT_TOKEN}/{{}}'

logger = logging.getLogger(__name__)


def send_request(endpoint, **kwargs):
    retry_count = 3
    response = requests.post(BASE_URL.format(endpoint), **kwargs)
    while not response.ok and retry_count > 0:
        if response.status_code == 429:
            timeout = response.json().get('parameters', {}).get('retry_after', 5)
            logger.warning('Too Many Requests, sleeping for %s', timeout)
            time.sleep(timeout)
            response = requests.post(BASE_URL.format(endpoint), **kwargs)
        elif response.status_code == 400:
            logger.warning('Bad request, retrying after 5s...')
            retry_count -= 1
            time.sleep(5)
            response = requests.post(BASE_URL.format(endpoint), **kwargs)
        else:
            logger.error('Error sending message: %s', response.text)
            return response

    return response


def notify_one(notification: NotificationBaseABC, force: bool = False):
    past_notifications = db['past_notifications']

    for chat_id in Settings.TG_CHAT_IDS:
        query = {
            'source': notification.source,
            'flat_id': notification.flat.flat_id,
            'chat_id': chat_id,
        }

        if not force and past_notifications.find_one(query):
            continue

        media, files = notification.request_data()

        notification_ts = datetime.now().timestamp()
        response = send_request(
            'sendMediaGroup',
            params={
                'chat_id': chat_id,
                'media': media,
            },
            files=files,
        )

        if response.ok:
            past_notifications.insert_one({
                **query,
                'notification_ts': notification_ts,
            })
            logger.info('Notified about flat, ID: %s', notification.flat.flat_id)
        else:
            logger.error('Failed to notify about flat, ID: %s', notification.flat.flat_id)


def notify_many(notifications: List[NotificationBaseABC], force: bool = False):
    for notification in notifications:
        notify_one(notification, force)
