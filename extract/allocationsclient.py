import requests
import os

class Client(requests.Session):
    """Class to encapsulate the rest api endpoint with a requests session.
    """
    def __init__(self, api_url=None, api_username=None,
                 api_password=None, *args, **kwargs):
        username = os.environ.get('NECTAR_ALLOCATIONS_USERNAME', api_username)
        password = os.environ.get('NECTAR_ALLOCATIONS_PASSWORD', api_password)
        self.api_url = os.environ.get('NECTAR_ALLOCATIONS_URL', api_url)
        assert username and password and self.api_url
        requests.Session.__init__(self, *args, **kwargs)
        self.auth = (username, password)

    def _api_get(self, rel_url, *args, **kwargs):
        return self.get("%s%s" % (self.api_url, rel_url), *args, **kwargs)

    def get_allocations(self):
        req = self._api_get('/rest_api/allocations')
        req.raise_for_status()
        return req.json()

    def get_quotas(self):
        req = self._api_get('/rest_api/quotas')
        req.raise_for_status()
        return req.json()

