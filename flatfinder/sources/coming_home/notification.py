from flatfinder.sources.base.notification import NotificationBaseABC, GOOGLE_MAPS_URL


class ComingHomeNotification(NotificationBaseABC):
    source = 'Coming-Home'

    _caption_template = '''From <a href="{url}">{source}</a>
<b>Price</b>: {price:.0f}
<b>Area</b>: {area}
<b>Rooms</b>: {rooms}
<b>District</b>: {district} (📍 <a href="{google_maps}">Location</a>)
<b>Available from</b>: {available_from}
<b>Available to</b>: {available_to}
<b>Min months</b>: {min_period}'''

    _caption_defaults = {
        'available_to': '-',
        'min_period': '-',
    }

    def _prepare_message(self) -> str:
        flat_attrs = self.flat.to_mongo()

        if 'available_from' in flat_attrs:
            flat_attrs['available_from'] = flat_attrs['available_from'].date()

        if 'available_to' in flat_attrs:
            flat_attrs['available_to'] = flat_attrs['available_to'].date()

        return self._caption_template.format(
            source=self.source,
            google_maps=GOOGLE_MAPS_URL.format(self.flat.lat, self.flat.lon),
            **{**self._caption_defaults, **flat_attrs},
        )
