from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Type

import requests

from flatfinder.sources.base.db import FlatSearchResultBase, FlatBase
from flatfinder.utils import retry


class FlatSourceBaseABC(ABC):
    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @property
    @abstractmethod
    def search_collection(self) -> Type[FlatSearchResultBase]:
        return FlatSearchResultBase

    @property
    @abstractmethod
    def flat_collection(self) -> Type[FlatBase]:
        pass

    @abstractmethod
    def search(self, filters: Dict[str, Any] = None, **kwargs) -> List[FlatSearchResultBase]:
        """Search for the list of apartments that meet criteria listed in the `filters` argument."""
        pass

    @abstractmethod
    def get_one(self, flat_id: Union[str, int], update: bool = False) -> FlatBase:
        """Get apartment info by its ID.

        :param flat_id: ID of the flat in the source.
        :param update: When `False` search for flat details in DB and return if found. When `True`
            force update from source.
        """
        pass

    @retry(exceptions=(requests.HTTPError,))
    def _request(self, method: str, url: str, params: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """Make request to the source's website with retries."""
        response = requests.request(method, url, params=params, **kwargs)
        response.raise_for_status()
        return response

    def _endpoint(self, *parts) -> str:
        """Construct the endpoint URL from `parts`."""
        return '/'.join(str(part).strip('/') for part in (self.url, *parts))

    def save_search(self, search_items: List[Dict[str, Any]]) -> List[FlatSearchResultBase]:
        """Save search results into DB and return list of saved objects."""
        flat_items = []
        for search_item in search_items:
            flat_items.append(
                self.search_collection.objects(flat_id=search_item['flat_id']).modify(
                    upsert=True,
                    new=True,
                    **search_item,
                )
            )

        return flat_items

    def save_flat(self, flat: Dict[str, Any]) -> FlatBase:
        """Save flat into DB."""
        return self.flat_collection.objects(flat_id=flat['flat_id']).modify(
            upsert=True,
            new=True,
            **flat
        )
