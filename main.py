import time
import argparse
import logging
from datetime import datetime
from typing import Dict, Type

from sources.base import FlatSourceABC
from sources.city_expert import CityExpert
from sources.halooglasi import HaloOglasi
from db import db
from bot import notify

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d' + time.strftime('%z') + ' - %(name)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SOURCE_TYPES: Dict[str, Type[FlatSourceABC]] = {
    'cityexpert': CityExpert,
    'halooglasi': HaloOglasi,
}


def is_flat_ok(flat):
    return flat['price'] < 1000 \
           and 30 <= flat['size'] < 120


def update_flats(source_name):
    source = SOURCE_TYPES[source_name]()
    current_ts = datetime.now().timestamp()
    flats = source.search()

    logger.info('%s apartments found in source', len(flats))

    source_collection = db[source_name]
    source_collection.create_index('id')

    detail_collection = db[source_name + '_detail']
    detail_collection.create_index('id')

    inserted = []
    for flat in flats:
        source_collection.update_one(
            {'id': flat['id']},
            {'$set': {**flat, 'updated_ts': current_ts}},
            upsert=True,
        )

        if is_flat_ok(flat):
            flat_detail = detail_collection.find_one({'id': flat['id']})
            if not flat_detail:
                logger.info('Downloading data for property_id: %s', flat['id'])
                flat_detail = source.get_one(flat['id'])
                detail_collection.insert_one(flat_detail)

            inserted.append(flat_detail)

    return inserted


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('-n', '--notify', action='store_true')
    parse.add_argument('source', type=str)
    args = parse.parse_args()

    inserted_flats = update_flats(args.source)
    if inserted_flats and args.notify:
        notify(inserted_flats, args.source)
