from typing import Union, List, Optional, Dict, Any

import requests

from flatfinder.sources.base.db import FlatBase, FlatSearchResultBase
from flatfinder.sources.base.filter import SearchFilter
from flatfinder.sources import FlatSourceBaseABC
from flatfinder.sources.coming_home.filter import ComingHomeFilter
from flatfinder.sources.coming_home.db import ComingHomeSearchResult, ComingHomeFlat


class ComingHome(FlatSourceBaseABC):
    search_collection = ComingHomeSearchResult
    flat_collection = ComingHomeFlat

    url = 'https://api.coming-home.com/'
    image_url = 'https://media.coming-home.com/bilder/maxi/{}.jpg'

    def __init__(self, base_filters: Optional[SearchFilter] = None):
        self.base_filters = ComingHomeFilter.from_instance(base_filters).to_dict()

    def _flat_url(self, flat_id: str) -> str:
        return self._endpoint('api', 'v1', 'property', flat_id) + '/'

    def _request(self, method: str, url: str, params: Dict[str, Any] = None, **kwargs) -> requests.Response:
        headers = {
            **kwargs.pop('headers', {}),
            'Accept-Language': 'en',
            'Authorization': 'Basic Y29taW5nOmNoMDgxNw==',
        }

        params = {
            **(params or {}),
            'lang': 'en',
            'camelize': 1,
        }

        return super()._request(method, url, params, headers=headers)

    def search(self, filters: Optional[SearchFilter] = None, **kwargs) -> List[FlatSearchResultBase]:
        filters = ComingHomeFilter.from_dict({
            **self.base_filters,
            **ComingHomeFilter.from_instance(filters).to_dict()
        })

        params = {
            'city': 'berlin,potsdam',
            'taxonomies': 1,
        }

        apartments = self._request('get', self._endpoint('api', 'v1', 'properties'), params=params).json().get('data')
        results = [{'flat_id': item['cid'], 'url': self._flat_url(item['cid'])}
                   for item in apartments
                   if filters.check_apartment(item)]
        return self.save_search(results)

    def get_one(self, flat_id: Union[str, int], update: bool = False) -> FlatBase:
        if update or not self.flat_collection.objects(flat_id=flat_id):
            flat_url = self._flat_url(flat_id)

            data = self._request('get', flat_url).json().get('data')
            flat = self.save_flat({
                'flat_id': str(data['cid']),
                'url': 'https://coming-home.com/en/living/{}'.format(data['cid']),
                'title': data.get('title'),
                'image_list': [self.image_url.format(img) for img in data.get('media', {}).get('images', [])],
                'lat': data.get('latitudeObfuscated'),
                'lon': data.get('longitudeObfuscated'),
                'rooms': data.get('rooms'),
                'area': data.get('squaremeter'),
                'price': data.get('rent'),
                'district': data.get('neighborhood'),
                'bedrooms': data.get('bedrooms'),
                'max_persons': data.get('persons'),
                'available_from': data.get('availableFrom'),
                'available_to': data.get('availableTo'),
                'min_period': data.get('periodMin'),
            })
        else:
            flat = self.flat_collection.objects.get(flat_id=flat_id)

        return flat
