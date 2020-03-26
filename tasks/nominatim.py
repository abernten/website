import requests

def find_coordinates(query):
    response = requests.get('https://nominatim.openstreetmap.org/search', params={
        'format': 'json',
        'q': query
    })

    if not response.status_code == requests.codes.ok:
        return False

    places = response.json()
    if len(places) > 0:
        place = places[0]
        return (place['lon'], place['lat'])
    return False
