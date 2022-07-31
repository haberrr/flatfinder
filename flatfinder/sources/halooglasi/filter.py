import logging
from dataclasses import dataclass

from flatfinder.filters import SearchFilter, Furnished

logger = logging.getLogger(__name__)


@dataclass
class HaloOglasiFilter(SearchFilter):
    furnished_map = {
        Furnished.furnished: 562,
        Furnished.semifurnished: 563,
        Furnished.unfurnished: 564,
    }

    def to_dict(self):
        if self.room_count is not None:
            logger.warning('HaloOglasi source currenlty does not support filtering by room count.')

        filters = {
            'cena_d_from': self.min_price,
            'cena_d_to': self.max_price,
            'kvadratura_d_from': self.min_area,
            'kvadratura_d_to': self.max_area,
            'namestenost_id_l': ','.join(str(self.furnished_map[f]) for f in self.furnished) if self.furnished else None
        }

        return {k: v for k, v in filters.items() if v is not None}
