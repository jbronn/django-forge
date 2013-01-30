"""
Tests for the Forge modules resource (/modules.json).
"""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson


class TestModulesResource(TestCase):

    def test_empty_query(self):
        """
        Ensure an empty list is returned when there are no Forge modules.
        """
        response = self.client.get(reverse('modules_json'))
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(simplejson.loads(response.content), [])
