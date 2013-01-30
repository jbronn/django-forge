"""
Tests for the Forge releases resource (/api/v1/releases.json).
"""
from django.core.urlresolvers import reverse
from django.test import TestCase


class TestReleasesResource(TestCase):

    def test_module_required(self):
        """
        Ensure the `module` GET parameter is required.
        """
        response = self.client.get(reverse('releases_json'))
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertContains(response,
                            '["Parameter module is required"]',
                            status_code=400)

    def test_invalid_module_name(self):
        """
        Ensure invalid module names aren't accepted.
        """
        invalid_names = ('invalidmodule', '$!?')
        for invalid_name in invalid_names:
            response = self.client.get(
                reverse('releases_json') + '?module=%s' % invalid_name
            )
            self.assertEqual(response['Content-Type'], 'application/json')
            self.assertContains(response, '["Invalid module name"]',
                                status_code=400)

    def test_module_not_found(self):
        """
        Ensure proper response and status code when module doesn't exist.
        """
        fake_module = 'puppetlabs/fakemod'
        response = self.client.get(
            reverse('releases_json') + '?module=%s' % fake_module
        )
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertContains(response, 'Module %s not found' % fake_module,
                            status_code=410)
