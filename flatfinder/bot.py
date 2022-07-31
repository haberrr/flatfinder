import io
import time
import json
import logging
from typing import List
from datetime import datetime

import requests

from flatfinder.db import db, FlatABC
from flatfinder.settings import Settings

BASE_URL = f'https://api.telegram.org/bot{Settings.TG_BOT_TOKEN}/{{}}'
GOOGLE_MAPS_URL = 'https://google.com/maps/search/?api=1&query={},{}'

CAPTION_TEMPLATE = '''From <a href="{url}">{source}</a>
<b>Price</b>: {price:.0f}
<b>Area</b>: {area}
<b>Rooms</b>: {rooms}
<b>District</b>: {district} (📍 <a href="{google_maps}">Location</a>)
<b>Views</b>: {views}
<b>Agency</b>: {advertiser}
'''

CAPTION_DEFAULTS = {
    'views': 'no info',
    'advertiser': 'no info',
}

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


def prepare_media(flat: FlatABC):
    media = []
    files = {}

    for i, image_src in enumerate(flat.image_list):
        if len(media) >= 10:
            break

        response = requests.get(image_src)
        if response.ok:
            media.append({
                'type': 'photo',
                'media': f'attach://image{i}',
            })
            files[f'image{i}'] = io.BytesIO(response.content)

    return media, files


def notify(flats: List[FlatABC], source):
    past_notifications = db['past_notifications']

    for flat in flats:
        for chat_id in Settings.TG_CHAT_IDS:
            if past_notifications.find_one({'source': source, 'flat_id': flat.flat_id, 'chat_id': chat_id}):
                continue

            media, files = prepare_media(flat)
            if len(media) == 0:
                continue

            media[0].update({
                'caption': CAPTION_TEMPLATE.format(
                    source=source.upper(),
                    google_maps=GOOGLE_MAPS_URL.format(flat.lat, flat.lon),
                    **{**CAPTION_DEFAULTS, **flat.to_mongo()},
                ),
                'parse_mode': 'HTML',
            })

            notification_ts = datetime.now().timestamp()
            response = send_request(
                'sendMediaGroup',
                params={
                    'chat_id': chat_id,
                    'media': json.dumps(media),
                },
                files=files,
            )

            if response.ok:
                past_notifications.insert_one({
                    'flat_id': flat.flat_id,
                    'source': source,
                    'notification_ts': notification_ts,
                    'chat_id': chat_id,
                })
                logger.info('Notified about flat, ID: %s', flat.flat_id)
            else:
                logger.error('Failed to notify about flat, ID: %s', flat.flat_id)
