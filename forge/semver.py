"""
Overloaded classes from the `semantic_version` library that can work with
the 'flavor' of semantic version specifications used by Puppet Labs.
"""
import re

from semantic_version import Spec, SpecItem, Version


class ForgeSpecItem(SpecItem):
    spec_pattern = r'(<|<=|==|>=|>|!=)\s?(\d[^\s]*)'
    re_spec = re.compile(r'^%s$' % spec_pattern)

    def __repr__(self):
        return '<ForgeSpecItem: %s %r>' % (self.kind, self.spec)

    def parse(self, requirement_string):
        if not requirement_string:
            raise ValueError(
                "Invalid empty requirement specification: %r" % requirement_string
            )

        # Special case: the 'any' version spec.
        if requirement_string == '*':
            return (self.KIND_ANY, '')

        # If a version is passed in, it
        if Version.version_re.match(requirement_string):
            requirement_string = self.KIND_EQUAL + requirement_string

        match = self.re_spec.match(requirement_string)
        if not match:
            raise ValueError(
                "Invalid requirement specification: %r" % requirement_string
            )

        kind, version = match.groups()
        spec = Version(version, partial=True)
        return (kind, spec)


class ForgeSpec(Spec):
    re_findall = re.compile(ForgeSpecItem.spec_pattern).findall

    # Regular expression for shorthand semantic version range acceptable
    # by Puppet Modules.
    re_shorthand = re.compile(r'^(\d+)\.(x|\d+\.x)$')

    def __init__(self, *specs_strings):
        subspecs = [self.parse(spec) for spec in specs_strings]
        self.specs = sum(subspecs, ())

    def __repr__(self):
        return '<ForgeSpec: %r>' % (self.specs,)

    def parse(self, specs_string):
        shorthand_match = self.re_shorthand.match(specs_string)
        if shorthand_match:
            major = int(shorthand_match.group(1))
            minor = shorthand_match.group(2)
            if minor == 'x':
                spec_texts = [
                    '%s%d.%d.%d' % (ForgeSpecItem.KIND_GTE, major, 0, 0),
                    '%s%d.%d.%d' % (ForgeSpecItem.KIND_LT, major+1, 0, 0)
                ]
            else:
                minor = int(minor.split('.')[0])
                spec_texts = [
                    '%s%d.%d.%d' % (ForgeSpecItem.KIND_GTE, major, minor, 0),
                    '%s%d.%d.%d' % (ForgeSpecItem.KIND_LT, major, minor+1, 0)
                ]
        elif ',' in specs_string:
            spec_texts = specs_string.split(',')
        elif ForgeSpecItem.re_spec.match(specs_string):
            spec_texts = [''.join(text_group) for text_group in
                          self.re_findall(specs_string)]
        else:
            spec_texts = [specs_string]
        return tuple(ForgeSpecItem(spec_text) for spec_text in spec_texts)
