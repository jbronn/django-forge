import json
import logging
import time
import urllib
import urlparse

import requests

from . import __version__
from . import constants


logger = logging.getLogger('forge.client')


class ForgeClient(object):

    def __init__(self, api_url=constants.PUPPETLABS_FORGE_API_URL,
                 api_version=3, agent_type=None, verify=True):
        """
        This is an object that acts as client for the Forge according
        to the given parameters.
        """
        # Use of Puppet Labs' forge requires a user agent:
        #  https://forgeapi.puppetlabs.com/#user-agent-required
        user_agent = 'django-forge/%s' % __version__
        if agent_type:
            user_agent += ' (%s)' % agent_type
        logger.info('setting client user agent to %s' % user_agent)
        self.user_agent = user_agent
        self.api_url = urlparse.urljoin(api_url, 'v%d/' % api_version)
        self.verify = verify

    def get(self, url, **headers):
        headers.setdefault('User-Agent', self.user_agent)
        return requests.get(url, headers=headers, verify=self.verify)


class ForgeAPI(object):
    def __init__(self, client, endpoint, limit=20, query=None, throttle=0):
        # Setting instance variables.
        self.client = client
        self.endpoint = endpoint
        self.limit = limit
        self.throttle = throttle
        self.query = query or {}

        # Joining the client's API URL with that of the given endpoint.
        self.api_url = urlparse.urljoin(self.client.api_url, self.endpoint)

        # Performing the initial API request to get the total object count and
        # prime the initial results.
        initial_data = self.request(self.url(**self.query))
        self.total = initial_data['pagination']['total']
        self.results = initial_data['results']

    def __iter__(self):
        query = self.query.copy()
        for idx in xrange(len(self)):
            if idx >= len(self.results):
                if self.throttle:
                    time.sleep(self.throttle)
                query['offset'] = idx
                data = self.request(self.url(**query))
                self.results.extend(data['results'])
            yield self.results[idx]

    def __len__(self):
        return self.total

    def request(self, url):
        logger.info('making API request: %s' % url)
        req = self.client.get(url)
        try:
            req.raise_for_status()
        except Exception as e:
            logger.exception(e)
            raise
        return json.loads(req.content)

    def url(self, **query):
        # Currently, the forge doesn't allow any modification to the limit.
        query['limit'] = self.limit
        splits = urlparse.urlsplit(self.api_url)
        return urlparse.urlunsplit(
            (splits.scheme, splits.netloc, splits.path,
             urllib.urlencode(query), splits.fragment)
        )
