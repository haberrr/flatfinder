from flatfinder.sources.base.notification import NotificationBaseABC


class CityExpertNotification(NotificationBaseABC):
    source = 'CityExpert'

    _caption_template = '''From <a href="{url}">{source}</a>
    <b>Price</b>: {price:.0f}
    <b>Area</b>: {area}
    <b>Rooms</b>: {rooms}
    <b>District</b>: {district} (📍 <a href="{google_maps}">Location</a>)
    '''
