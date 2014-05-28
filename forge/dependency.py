from collections import defaultdict

from .models import Module, Release
from .semver import ForgeSpec


def release_specs(release, forgespec=True):
    """
    For the given release, return a list of all the dependencies as 2-tuples,
    comprising the module name and dependency specification (as ForgeSpec).
    """
    specs = []
    for depend in release.metadata.get('dependencies', []):
        spec = depend.get('version_requirement', '>= 0.0.0')
        if forgespec: spec = ForgeSpec(spec)
        specs.append((depend['name'], spec))
    return specs


def calculate_dependencies(release):
    queue = set([release])
    dependencies = defaultdict(set)
    dependencies[unicode(release.module)].add(
        ForgeSpec(str(release.version))
    )

    while queue:
        rel = queue.pop()
        for dep_item in release_specs(rel):
            dep_mod, dep_spec = dep_item
            if not dep_spec in dependencies[dep_mod]:
                dependencies[dep_mod].add(dep_spec)
                try:
                    for dep_rel in Module.get_for_full_name(dep_mod).releases.all():
                        if dep_rel.version in dep_spec:
                            queue.add(dep_rel)
                except Module.DoesNotExist:
                    raise Exception('Dependency module %s not found' % dep_mod)

    return dependencies


def release_dependencies(release):
    """
    This determines the dependencies for the given module release.
    """
    dependency_specs = calculate_dependencies(release)
    dependencies = defaultdict(list)

    for depend, specs in dependency_specs.iteritems():
        try:
            mod = Module.get_for_full_name(depend)
        except Module.DoesNotExist:
            raise Exception('Dependency module %s not found' % depend)
        releases = []
        for rel in mod.releases.all():
            if all([rel.version in spec for spec in specs]):
                dependencies[depend].append({
                        'version': str(rel.version),
                        'file': rel.tarball.url,
                        'dependencies': release_specs(rel, forgespec=False),
                })

    return dependencies
