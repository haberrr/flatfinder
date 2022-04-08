import re
import json
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from sources.base import FlatSourceBase


class HaloOglasi(FlatSourceBase):
    url = 'https://www.halooglasi.com/'
    img_url = 'https://img.halooglasi.com/'
    default_filters = {
        'stanje_objekta_id_l': ','.join(['370347', '11950001']),  # renovated, lux
        'namestenost_id_l': 562,  # furnished
        'cena_d_from': 350,
        'cena_d_to': 1000,
        'cena_d_unit': 4,
        'kvadratura_d_from': 30,
        'kvadratura_d_unit': 1,
    }

    def __init__(self, base_filters=None, search_depth=3):
        self.base_filters = {
            **self.default_filters,
            **(base_filters or {}),
        }
        self.search_depth = search_depth

    def _parse_serp(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        flat_list = []
        for flat in soup.find('div', class_='row product-list').find_all('div', class_='product-item'):
            if 'banner-list' not in flat.get('class'):
                info = {item.find('span').text: list(item.children)[0].contents[0] for item in
                        flat.find(class_='product-features').find_all('li')}

                flat_list.append({
                    'id': flat.get('id'),
                    'url': self._endpoint(flat.find(class_='pi-img-wrapper').find('a').get('href')),
                    'title': flat.find(class_='product-title').text,
                    'price': float(flat.find(class_='central-feature').text.split()[0]),
                    'location': [part.text.strip() for part in flat.find(class_='subtitle-places').find_all('li')],
                    'size': int(info['Kvadratura'].split()[0]),
                    'rooms': info['Broj soba'].split()[0],
                })

        return flat_list

    def _endpoint(self, *parts):
        return '/'.join(str(part).strip('/') for part in (self.url, *parts))

    def search(self, filters=None):
        filters = filters or {}

        results = []
        for page in range(1, self.search_depth + 1):
            response = self._request('get', self._endpoint('nekretnine', 'izdavanje-stanova', 'beograd'), params={
                **self.base_filters,
                **filters,
                'page': page,
            })
            results.extend(self._parse_serp(response.text))

        return results

    def get_one(self, flat_id):
        response = self._request('get', self._endpoint('nekretnine', 'izdavanje-stanova', 'beograd', flat_id))
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.find('script', text=re.compile('QuidditaEnvironment.CurrentClassified={\"'))

        match = re.search('QuidditaEnvironment\.CurrentClassified=({.*?});', str(data))
        if match:
            result = json.loads(match.group(1))
            return {
                'id': flat_id,
                'url': self._endpoint('nekretnine', 'izdavanje-stanova', 'beograd', flat_id),
                'image_list': [urljoin(self.img_url, img) for img in result['ImageURLs']],
                'title': result['Title'],
                'lat': float(result['GeoLocationRPT'].split(',')[0]),
                'lon': float(result['GeoLocationRPT'].split(',')[1]),
                'views': result['TotalViews'],
                'rooms': result['OtherFields']['broj_soba_s'],
                'size': result['OtherFields']['kvadratura_d'],
                'price': result['OtherFields']['cena_d'],
                'district': '{}, {}'.format(result['OtherFields']['lokacija_s'],
                                            result['OtherFields']['mikrolokacija_s']),
            }
        else:
            return {}
