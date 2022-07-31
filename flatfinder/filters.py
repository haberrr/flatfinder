from typing import Optional, List
from enum import Enum
from dataclasses import dataclass, asdict


class Furnished(Enum):
    unfurnished = 0
    semifurnished = 1
    furnished = 2


@dataclass
class SearchFilter:
    """Standardised filter with which every source must adhere."""
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    room_count: Optional[List[float]] = None
    furnished: Optional[List[Furnished]] = None

    @classmethod
    def from_instance(cls, instance: Optional['SearchFilter'] = None, **kwargs):
        if instance is not None:
            return cls(**asdict(instance), **kwargs)
        else:
            return cls(**kwargs)
