from django.test import TestCase

from forge.semver import ForgeSpec, ForgeSpecItem
from semantic_version import Version


class TestForgeSpec(TestCase):

    def test_spaces_in_spec_item(self):
        """
        Ensure that `ForgeSpecItem` is able to handle spaces (unlike SpecItem).
        """
        fsi = ForgeSpecItem('>= 1.0.0')
        self.assertEqual(fsi.kind, ForgeSpecItem.KIND_GTE)
        self.assertEqual(fsi.spec, Version('1.0.0', partial=True))

    def test_spaces_in_spec(self):
        """
        Ensure that `ForgeSpec` is able to tolerate spaces (unlike Spec).
        """
        # Have space in first range, but not in second.

        fs = ForgeSpec('>= 3.1.0 <4.0.0')
        self.assertEqual(fs.specs[0].kind, ForgeSpecItem.KIND_GTE)
        self.assertEqual(fs.specs[0].spec, Version('3.1.0', partial=True))
        self.assertEqual(fs.specs[1].kind, ForgeSpecItem.KIND_LT)
        self.assertEqual(fs.specs[1].spec, Version('4.0.0', partial=True))

    def test_shorthand_ranges(self):
        """
        Ensure that `ForgeSpec` accepts PuppetLabs' shorthand range notation.
        """
        # This should be shorthand for '>=4.0.0 <5.0.0'.
        fs = ForgeSpec('4.x')
        self.assertEqual(len(fs.specs), 2)
        self.assertEqual(fs.specs[0].kind, ForgeSpecItem.KIND_GTE)
        self.assertEqual(fs.specs[0].spec, Version('4.0.0', partial=True))
        self.assertEqual(fs.specs[1].kind, ForgeSpecItem.KIND_LT)
        self.assertEqual(fs.specs[1].spec, Version('5.0.0', partial=True))

        # This should be shorthand for '>=1.2.0 <1.3.0'.
        fs = ForgeSpec('1.2.x')
        self.assertEqual(len(fs.specs), 2)
        self.assertEqual(fs.specs[0].kind, ForgeSpecItem.KIND_GTE)
        self.assertEqual(fs.specs[0].spec, Version('1.2.0', partial=True))
        self.assertEqual(fs.specs[1].kind, ForgeSpecItem.KIND_LT)
        self.assertEqual(fs.specs[1].spec, Version('1.3.0', partial=True))
