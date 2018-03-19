import requests

class SubregionManager():

    @staticmethod
    def get_available_resolutions():
        r = requests.get('http://fortroute.com/subregions/available')
        if r.status_code == 200:
            return sorted(r.json(), reverse=True)
        else:
            return []
    
    @staticmethod
    def get_minimap_subregion(resolution, hud_scale=100):
        url = 'http://fortroute.com/subregions/minimap/{}/{}'.format(resolution, hud_scale)
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return []
