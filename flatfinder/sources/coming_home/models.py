from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Dict, Any

from dacite import from_dict, Config


@dataclass
class ComingHomeFlatRaw:
    rent: int
    squaremeter: int
    personsMax: int
    rooms: float
    bedrooms: int
    baths: int
    availableFrom: date
    availableTo: Optional[date] = None
    extraHandles: Optional[List[str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        config = Config(
            type_hooks={
                date: lambda x: datetime.strptime(x, '%Y-%m-%d').date(),
            },
            cast=[int, float],
        )

        return from_dict(cls, data, config)
