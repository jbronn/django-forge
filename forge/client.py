import json
import requests
import time
import urllib
import urlparse

from . import __version__
from . import constants


class ForgeClient(object):

    def __init__(self, api_url=PUPPETLABS_FORGE_API_URL,
                 api_version=3, agent_type=None):
        """
        TODO
        """
        # Use of Puppet Labs' forge requires a user agent is set:
        #  https://forgeapi.puppetlabs.com/#user-agent-required
        user_agent = 'django-forge/%s' % __version__
        if agent_type:
            user_agent += ' (%s)' % agent_type
        self.user_agent = user_agent
        self.api_url = '%s/v%d/' % (api_url, api_version)

    def get(self, url, headers=None):
        request_headers = {
            'User-Agent': self.user_agent,
        }
        if headers:
            request_headers.update(headers)

        return requests.get(url, headers=request_headers)


class ForgeAPI(object):
    def __init__(self, client, endpoint, limit=20, throttle=0):
        # Setting instance variables.
        self.client = client
        self.endpoint = endpoint
        self.limit = limit
        self.throttle = throttle

        # Joining the client's API URL with that of the given endpoint.
        self.api_url = urlparse.urljoin(self.client.api_url, self.endpoint)

        # Performing the initial API request to get the total object count and
        # prime the initial results.
        initial_data = self.api_request(self.url())
        self.total = initial_data['pagination']['total']
        self.results = initial_data['results']

    def __iter__(self):
        for idx in xrange(len(self)):
            if idx >= len(self.results):
                if self.throttle:
                    time.sleep(self.throttle)
                data = self.api_request(self.url(offset=idx))
                self.results.extend(data['results'])
            yield self.results[idx]

    def __len__(self):
        return self.total

    def api_request(self, url):
        req = self.client.get(url)
        if not req.status_code == 200:
            raise Exception('Could not perform Forge API request.')
        return json.loads(req.content)

    def url(self, offset=0):
        splits = urlparse.urlsplit(self.api_url)
        query = urllib.urlencode({'limit': self.limit, 'offset': offset})
        return urlparse.urlunsplit(
            (splits.scheme, splits.netloc, splits.path,
             query, splits.fragment)
        )
