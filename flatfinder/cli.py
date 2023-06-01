import time
import argparse
import logging
from datetime import date
from typing import Dict, Type, List, Any

from flatfinder.sources import FlatSourceBaseABC, SearchFilter, FlatBase, NotificationBaseABC
from flatfinder.sources import cityexpert, halooglasi, nekretnine, coming_home
from flatfinder.telegram.bot import notify_many

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d' + time.strftime('%z') + ' - %(name)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def update_flats(source: FlatSourceBaseABC, filters: Dict[str, Any] = None) -> List[FlatBase]:
    """Update list of flats from the source defined by the `source_name` and return it.

    :param source: Source from which to find the apartments.
    :param filters: Filters to use, when searching for apartments in source.
    :return: List of apartments according to filters.
    """
    flats = source.search(filters=filters)

    logger.info('%s apartments found in source', len(flats))

    flat_details = []
    for flat in flats:
        flat_details.append(source.get_one(flat_id=flat.flat_id))

    return flat_details


def _main():
    parse = argparse.ArgumentParser()
    parse.add_argument('-n', '--notify', action='store_true')
    parse.add_argument('-f', '--force', action='store_true')
    parse.add_argument('source', type=str)
    args = parse.parse_args()

    SOURCE_TYPES: Dict[str, Type[FlatSourceBaseABC]] = {
        'cityexpert': cityexpert.Source,
        'halooglasi': halooglasi.Source,
        'nekretnine': nekretnine.Source,
        'coming_home': coming_home.Source,
    }

    FILTERS: Dict[str, SearchFilter] = {
        'coming_home': coming_home.Filter(
            max_price=1500,
            check_in_date=date(2023, 7, 1),
            persons=2,
            cats=True,
        ),
    }

    NOTIFICATIONS_TYPES: Dict[str, Type[NotificationBaseABC]] = {
        'cityexpert': cityexpert.Notification,
        'halooglasi': halooglasi.Notification,
        'nekretnine': nekretnine.Notification,
        'coming_home': coming_home.Notification,
    }

    source = SOURCE_TYPES[args.source]()
    filters = FILTERS.get(args.source)
    notification_type = NOTIFICATIONS_TYPES[args.source]

    inserted_flats = update_flats(source, filters=filters)

    if inserted_flats and args.notify:
        notify_many(
            [notification_type(flat) for flat in inserted_flats],
            args.force,
        )


if __name__ == '__main__':
    _main()
