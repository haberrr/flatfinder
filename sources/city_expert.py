import json

import requests

from sources.base import FlatSourceBase

PTID_MAP = {
    1: 'apartment',
    2: 'house',
    3: 'apartment-in-house',
    4: 'shop',
    5: 'office-space',
}


def _make_flat_url(flat):
    rooms = flat['structure'].replace('+', '').replace('.', '').lower()
    if rooms != 'other':
        rooms = '{}-rooms'.format(rooms)

    return '{rooms}-{type}-{street}'.format(
        rooms=rooms,
        type=PTID_MAP[flat['ptId']],
        street=flat['street'].replace(' ', '-').lower(),
        municipality=flat['municipality'].replace(' ', '-').lower(),
    )


class CityExpert(FlatSourceBase):
    url = 'https://cityexpert.rs/'
    img_url = 'https://img.cityexpert.rs/sites/default/files/styles/1920x/public/image/{}'
    default_filters = {
        'ptId': [1, 2, 3],
        'cityId': 1,
        'rentOrSale': 'r',
        'currentPage': 1,
        'resultsPerPage': 100,
        'sort': 'datedsc',
        'furnished': [1],
        'structure': ['1.0', '1.5', '2.0', '2.5', '3.0', '3.5'],
    }

    def __init__(self, base_filters=None):
        self.base_filters = {
            **self.default_filters,
            **(base_filters or {}),
        }

    def _endpoint(self, *parts):
        return '/'.join(str(part).strip('/') for part in (self.url, *parts))

    def search(self, filters=None):
        def parse_results(items):
            return [{
                **item,
                'id': item['propId'],
            } for item in items]

        filters = filters or {}

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

        return results

    def get_one(self, flat_id):
        result = self._request('get', self._endpoint('api', 'PropertyView', flat_id, 'r')).json()
        result['id'] = result['propId']
        return {
            'id': flat_id,
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
        }
