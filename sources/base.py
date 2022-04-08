from abc import ABC, abstractmethod

import requests

from utils import retry


class FlatSourceABC(ABC):
    @abstractmethod
    def search(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_one(self, flat_id):
        pass


class FlatSourceBase(FlatSourceABC):
    def search(self, *args, **kwargs):
        raise NotImplementedError

    def get_one(self, flat_id):
        raise NotImplementedError

    @retry(exceptions=(requests.HTTPError,))
    def _request(self, method, url, params=None, **kwargs):
        response = requests.request(method, url, params=params, **kwargs)
        response.raise_for_status()
        return response
