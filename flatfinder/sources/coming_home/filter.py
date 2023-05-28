from datetime import date
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, asdict

from dacite import from_dict

from flatfinder.sources.base.filter import SearchFilter
from flatfinder.sources.coming_home.models import ComingHomeFlatRaw


@dataclass
class ComingHomeFilter(SearchFilter):
    persons: int = 1
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    cats: Optional[bool] = None

    def check_apartment(self, raw_apartment: Union[Dict[str, Any], ComingHomeFlatRaw]) -> bool:
        if not isinstance(raw_apartment, ComingHomeFlatRaw):
            raw_apartment = ComingHomeFlatRaw.from_dict(raw_apartment)

        return (
                (self.min_price or 0) <= raw_apartment.rent <= (self.max_price or float('inf'))
                and (self.min_area or 0) <= raw_apartment.squaremeter <= (self.max_area or float('inf'))
                and (self.persons <= raw_apartment.personsMax)
                and (self.room_count is None
                     or raw_apartment.rooms in self.room_count)
                and (self.check_in_date is None
                     or self.check_in_date >= raw_apartment.availableFrom)
                and (self.check_out_date is None
                     or raw_apartment.availableTo is None
                     or self.check_out_date <= raw_apartment.availableTo)
                and (self.cats is None
                     or self.cats == ('cats' in raw_apartment.extraHandles))
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComingHomeFilter':
        return from_dict(cls, data)
