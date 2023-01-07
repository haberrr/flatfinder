import re
import json
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from flatfinder.sources.base import FlatSourceBaseABC
from flatfinder.db import FlatSearchResultABC, FlatABC
from flatfinder.sources.halooglasi.filter import HaloOglasiFilter


class HaloOglasiFlatSearchResult(FlatSearchResultABC):
    pass


class HaloOglasiFlat(FlatABC):
    pass


class HaloOglasi(FlatSourceBaseABC):
    search_collection = HaloOglasiFlatSearchResult
    flat_collection = HaloOglasiFlat

    url = 'https://www.halooglasi.com/'
    img_url = 'https://img.halooglasi.com/'
    default_filters = {
        'stanje_objekta_id_l': ','.join(['370347', '11950001']),  # renovated, lux
        'namestenost_id_l': 562,  # furnished
        'cena_d_from': 200,
        'cena_d_to': 1000,
        'cena_d_unit': 4,
        'kvadratura_d_from': 30,
        'kvadratura_d_unit': 1,
    }

    def __init__(self, base_filters=None, default_depth=3):
        self.base_filters = {
            **self.default_filters,
            **HaloOglasiFilter.from_instance(base_filters).to_dict(),
        }
        self.default_depth = default_depth

    def _parse_serp(self, html):
        soup = BeautifulSoup(html, 'html.parser')

        flat_list = []
        for flat in soup.find('div', class_='row product-list').find_all('div', class_='product-item'):
            if 'banner-list' not in flat.get('class'):
                flat_list.append({
                    'flat_id': flat.get('id'),
                    'url': self._endpoint(flat.find(class_='pi-img-wrapper').find('a').get('href')),
                })

        return flat_list

    def search(self, filters=None, depth=None):
        filters = HaloOglasiFilter.from_instance(filters).to_dict()
        depth = depth or self.default_depth

        results = []
        for page in range(1, depth + 1):
            response = self._request('get', self._endpoint('nekretnine', 'izdavanje-stanova', 'beograd'), params={
                **self.base_filters,
                **filters,
                'page': page,
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
        response = self._request('get', self._endpoint('nekretnine', 'izdavanje-stanova', 'beograd', flat_id))
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.find('script', text=re.compile('QuidditaEnvironment.CurrentClassified={\"'))

        flat_data = {}
        if match := re.search('QuidditaEnvironment\.CurrentClassified=({.*?});', str(data)):
            result = json.loads(match.group(1))
            flat_data.update({
                'flat_id': flat_id,
                'url': self._endpoint('nekretnine', 'izdavanje-stanova', 'beograd', flat_id),
                'image_list': [urljoin(self.img_url, img) for img in result['ImageURLs']],
                'title': result['Title'],
                'lat': float(result['GeoLocationRPT'].split(',')[0]),
                'lon': float(result['GeoLocationRPT'].split(',')[1]),
                'views': result['TotalViews'],
                'rooms': result['OtherFields']['broj_soba_s'],
                'area': result['OtherFields']['kvadratura_d'],
                'price': result['OtherFields']['cena_d'],
                'district': '{}, {}'.format(result['OtherFields']['lokacija_s'],
                                            result['OtherFields']['mikrolokacija_s']),
            })

        if match := re.search('QuidditaEnvironment\.CurrentContactData=({.*?});', str(data)):
            result = json.loads(match.group(1))
            flat_data['advertiser'] = result['Advertiser']['DisplayName']

            contact_infos = result['Advertiser']['ContactInfos']
            try:
                flat_data['phone_numbers'] = [contact_infos[0][k] for k in ['Phone1', 'Phone2']
                                              if contact_infos[0].get(k) is not None]
            except IndexError:
                pass

        return flat_data
