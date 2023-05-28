from dataclasses import dataclass

from flatfinder.sources.base.filter import SearchFilter, Furnished


@dataclass
class CityExpertFilter(SearchFilter):
    furnished_map = {
        Furnished.furnished: 1,
        Furnished.semifurnished: 2,
        Furnished.unfurnished: 3,
    }

    def to_dict(self):
        filters = {
            'minPrice': self.min_price,
            'maxPrice': self.max_price,
            'minSize': self.min_area,
            'maxSize': self.max_area,
            'structure': [str(c) for c in self.room_count] if self.room_count else None,
            'furnished': [self.furnished_map[f] for f in self.furnished] if self.furnished else None,
        }

        return {k: v for k, v in filters.items() if v is not None}
