import re

from bs4 import BeautifulSoup

from flatfinder.sources.base import FlatSourceBaseABC
from flatfinder.db import FlatSearchResultABC, FlatABC
from .filter import NekretnineFilter


class NekretnineFlatSearchResult(FlatSearchResultABC):
    pass


class NekretnineFlat(FlatABC):
    pass


class Nekretnine(FlatSourceBaseABC):
    search_collection = NekretnineFlatSearchResult
    flat_collection = NekretnineFlat

    url = 'https://www.nekretnine.rs/'
    default_filters = {
        'stambeni-objekti': 'stanovi',
        'izdavanje-prodaja': 'izdavanje',
        'grad': 'beograd',
        'cena': '200_1000',
        'kvadratura': '30_',
        'opremljenost-nekretnine': '_'.join([  # everything except 'unfurnished'
            'standardno',
            'iznad-standarda',
            'prema-zahtevima',
            'namesten-bez-uredaja',
            'namesten-sa-uredajima'
        ]),
    }

    def __init__(self, base_filters=None, default_depth=2):
        self.base_filters = {
            **self.default_filters,
            **NekretnineFilter.from_instance(base_filters).to_dict(),
        }
        self.default_depth = default_depth

    def _url_from_filters(self, filters):
        filters = {
            **self.base_filters,
            **filters,
        }

        return [f'{k}/{v}' for k, v in filters.items()]

    def _parse_serp(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        flat_list = []
        for flat in soup.find('div', class_='advert-list').find_all('div', class_='row offer'):
            offer_title = flat.find('h2', class_='offer-title')
            flat_list.append({
                'flat_id': offer_title.find('a').get('href').strip('/').split('/')[-1],
                'url': self._endpoint(offer_title.find('a').get('href')),
            })

        return flat_list

    def search(self, filters=None, depth=None):
        filters = NekretnineFilter.from_instance(filters).to_dict()
        depth = depth or self.default_depth

        results = []
        for page in range(1, depth + 1):
            response = self._request('get', self._endpoint(*self._url_from_filters({
                **filters,
                'stranica': page,
            })), params={
                'order': '2',
            })
            results.extend(self._parse_serp(response.text))

        return self.save_search(results)

    def get_one(self, flat_id, update=False):
        if update or not self.flat_collection.objects(flat_id=flat_id):
            flat = self.save_flat(self._get_one_from_source(flat_id))
        else:
            flat = self.flat_collection.objects.get(flat_id=flat_id)

        return flat

    def _get_one_from_source(self, flat_id):
        def safe_convert(value, type_):
            try:
                return type_(value)
            except (ValueError, IndexError):
                pass

        response = self._request('get', self._endpoint(flat_id))
        soup = BeautifulSoup(response.text, 'html.parser')

        gallery_response = self._request('get', response.url + 'galerija')
        gallery_soup = BeautifulSoup(gallery_response.text, 'html.parser')

        details = soup.find('div', class_='property__main-details').find_all('li')

        return {
            'flat_id': flat_id,
            'url': response.url,
            'image_list': [img.get('src') for img in gallery_soup.find('div', class_='gallery-top').find_all('img')],
            'title': soup.find('h1', class_='detail-title').text.strip(),
            'lat': float(m.group(1)) if (m := re.search(r'ppLat = ([\d.]*)', response.text)) else None,
            'lon': float(m.group(1)) if (m := re.search(r'ppLng = ([\d.]*)', response.text)) else None,
            'rooms': safe_convert(details[1].text.strip().split(':')[1], float),
            'area': safe_convert(details[0].text.strip().split(':')[1].split()[0], float),
            'price': safe_convert(soup.find('h4', class_='stickyBox__price').text.split()[0], float),
            'district': ', '.join(
                [item.text for item in soup.find('div', class_='property__location').find_all('li')[-2:]]
            ),
            'advertiser': soup.find('div', class_='contact-card').find('h4', class_='name').text,
        }
