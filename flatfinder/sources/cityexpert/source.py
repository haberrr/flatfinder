import json
from typing import Optional

from flatfinder.sources.base import FlatSourceBaseABC
from flatfinder.db import FlatSearchResultABC, FlatABC
from flatfinder.filters import SearchFilter
from .filter import CityExpertFilter


class CityExpertFlatSearchResult(FlatSearchResultABC):
    pass


class CityExpertFlat(FlatABC):
    pass


class CityExpert(FlatSourceBaseABC):
    search_collection = CityExpertFlatSearchResult
    flat_collection = CityExpertFlat

    url = 'https://cityexpert.rs/'
    img_url = 'https://img.cityexpert.rs/sites/default/files/styles/1920x/public/image/{}'
    default_filters = {
        'ptId': [1, 2, 3],
        'cityId': 1,
        'rentOrSale': 'r',
        'currentPage': 1,
        'resultsPerPage': 100,
        'minPrice': 200,
        'maxPrice': 1000,
        'sort': 'datedsc',
        'furnished': [1],
        'structure': ['1.0', '1.5', '2.0', '2.5', '3.0', '3.5'],
    }

    def __init__(self, base_filters: Optional[SearchFilter] = None):
        self.base_filters = {
            **self.default_filters,
            **CityExpertFilter.from_instance(base_filters).to_dict(),
        }

    def search(self, filters: Optional[SearchFilter] = None, **kwargs):
        def parse_results(items):
            return [{
                'flat_id': str(item['propId']),
            } for item in items]

        filters = CityExpertFilter.from_instance(filters).to_dict()

        response = self._request('get', self._endpoint('api', 'Search'), params={
            'req': json.dumps({**self.base_filters, **filters}),
        }).json()
        results = parse_results(response['result'])

        page = 1
        while response['info'].get('hasNextPage', False):
            page += 1
            response = self._request('get', self._endpoint('api', 'Search'), params={
                'req': json.dumps({**self.base_filters, **filters, 'currentPage': page})
            }).json()

            results.extend(parse_results(response['result']))

        return self.save_search(results)

    def get_one(self, flat_id: str, update: bool = False) -> CityExpertFlat:
        if update or not self.flat_collection.objects(flat_id=flat_id):
            result = self._request('get', self._endpoint('api', 'PropertyView', flat_id, 'r')).json()
            flat = self.save_flat({
                'flat_id': flat_id,
                'url': self._endpoint('en/properties-for-rent/belgrade', flat_id, 'a'),
                'image_list': [self.img_url.format(img) for img in result['onsite']['imgFiles']],
                'title': result['street'],
                'lat': result['mapLat'],
                'lon': result['mapLng'],
                'views': None,
                'rooms': result['structure'],
                'size': result['size'],
                'price': result['price'],
                'district': result['municipality'],
            })
        else:
            flat = self.flat_collection.objects.get(flat_id=flat_id)

        return flat
