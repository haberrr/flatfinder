import logging
from dataclasses import dataclass

from flatfinder.filters import SearchFilter, Furnished

logger = logging.getLogger(__name__)


@dataclass
class NekretnineFilter(SearchFilter):
    furnished_map = {
        Furnished.furnished: 562,
        Furnished.semifurnished: 563,
        Furnished.unfurnished: 564,
    }

    room_count_map = {
        0: 'garsonjera',
        1: 'jednosoban-stan',
        2: 'dvosoban-stan',
        3: 'trosoban-stan',
        4: 'cetvorosoban-stan',
        5: 'petosoban-stan',
    }

    def to_dict(self):
        rooms = []
        if self.room_count:
            for cnt in self.room_count:
                if cnt > 5:
                    logger.warning(
                        'Nekretnine source: room count greater than or equal to 5 falls within the same filter group.')
                if cnt % 1:
                    logger.warning('Nekretnine source does not support fractional room count, rounding down.')
                rooms.append(self.room_count_map[max(min(int(cnt), 5), 0)])

            if len(rooms) == 6:
                rooms = []

        filters = {
            'cena': '{}_{}'.format(self.min_price or '',
                                   self.max_price or '') if self.min_price or self.max_price else None,
            'kvadratura': '{}_{}'.format(self.min_area or '',
                                         self.max_area or '') if self.min_area or self.max_area else None,
            'namestenost_id_l': ','.join(
                str(self.furnished_map[f]) for f in self.furnished) if self.furnished else None,
            'tip-stanovi': '_'.join(rooms) if rooms else None,
        }

        return {k: v for k, v in filters.items() if v is not None}
