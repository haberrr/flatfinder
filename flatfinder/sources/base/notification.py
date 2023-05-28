import io
import json
from abc import abstractmethod, ABC
from typing import List, Optional, Dict, Tuple

import requests

from flatfinder.sources.base.db import FlatBase

GOOGLE_MAPS_URL = 'https://google.com/maps/search/?api=1&query={},{}'


class NotificationBaseABC(ABC):
    _caption_template = '''From <a href="{url}">{source}</a>
<b>Price</b>: {price:.0f}
<b>Area</b>: {area}
<b>Rooms</b>: {rooms}
<b>District</b>: {district} (📍 <a href="{google_maps}">Location</a>)
<b>Views</b>: {views}
<b>Agency</b>: {advertiser}'''

    _caption_defaults = {
        'views': 'no info',
        'advertiser': 'no info',
    }

    @property
    @abstractmethod
    def source(self) -> str:
        pass

    def __init__(self, flat: FlatBase):
        self.flat: FlatBase = flat
        self.images: Optional[List[bytes]] = None

    def _download_media(self) -> None:
        images = []
        for image_url in self.flat.image_list:
            if len(images) >= 10:
                break

            response = requests.get(image_url)
            images.append(response.content)

        self.images = images

    def _prepare_media(self) -> Tuple[List[Dict[str, str]], Dict[str, io.BytesIO]]:
        if self.images is None:
            self._download_media()

        media = []
        files = {}

        for i, image in enumerate(self.images):
            media.append({
                'type': 'photo',
                'media': f'attach://image{i}',
            })
            files[f'image{i}'] = io.BytesIO(image)

        return media, files

    def _prepare_message(self) -> str:
        return self._caption_template.format(
            source=self.source,
            google_maps=GOOGLE_MAPS_URL.format(self.flat.lat, self.flat.lon),
            **{**self._caption_defaults, **self.flat.to_mongo()},
        )

    def request_data(self) -> Tuple[str, Dict[str, io.BytesIO]]:
        media, files = self._prepare_media()
        message = self._prepare_message()

        assert len(media) >= 2, 'Not enough media files'

        media[0].update({
            'caption': message,
            'parse_mode': 'HTML',
        })

        return json.dumps(media), files
