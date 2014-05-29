"""
Tests for the Forge modules resource (/modules.json).
"""
import json

from django.core.urlresolvers import reverse
from django.test import TestCase


class TestModulesResourceV1(TestCase):

    def test_empty_query(self):
        """
        Ensure an empty list is returned when there are no Forge modules.
        """
        response = self.client.get(reverse('modules_json_v1'))
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(json.loads(response.content), [])
