import time
import argparse
import logging
from typing import Dict, Type, List, Any

from flatfinder.sources import FlatSourceBaseABC, CityExpert, HaloOglasi, Nekretnine
from flatfinder.db import FlatABC
from flatfinder.bot import notify

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d' + time.strftime('%z') + ' - %(name)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def update_flats(source: FlatSourceBaseABC, filters: Dict[str, Any] = None) -> List[FlatABC]:
    """Update list of flats from the source defined by the `source_name` and return it.

    :param source: Source from which to find the apartments.
    :param filters: Filters to use, when searching for apartments in source.
    :return: List of apartments according to filters.
    """
    flats = source.search(filters=filters)

    logger.info('%s apartments found in source', len(flats))

    to_notify = []
    for flat in flats:
        to_notify.append(source.get_one(flat_id=flat.flat_id))

    return to_notify


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('-n', '--notify', action='store_true')
    parse.add_argument('source', type=str)
    args = parse.parse_args()

    SOURCE_TYPES: Dict[str, Type[FlatSourceBaseABC]] = {
        'cityexpert': CityExpert,
        'halooglasi': HaloOglasi,
        'nekretnine': Nekretnine,
    }

    inserted_flats = update_flats(SOURCE_TYPES[args.source]())
    if inserted_flats and args.notify:
        notify(inserted_flats, args.source)
