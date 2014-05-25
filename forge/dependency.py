from collections import defaultdict

from .models import Module


def module_dependencies(module, release=None):
    """
    This determines the dependencies for the given module.
    """
    dependencies = defaultdict(list)
    queue = set()

    def populate_dependencies(mod, rel=None):
        if rel is None:
            rel = mod.latest_release

        release_dependencies = [
            (depend['name'], depend.get('version_requirement', '>= 0.0.0'))
            for depend in rel.metadata.get('dependencies', [])
        ]
        full_name = str(rel.module)
        release_info = {
            'version': str(rel.version),
            'file': rel.tarball.url,
            'dependencies': release_dependencies,
        }

        dependencies[full_name].append(release_info)

        for name, version in release_dependencies:
            if not name in dependencies:
                queue.add(name)

    # Keep going until we don't have any dependencies left.
    populate_dependencies(module, release)
    while queue:
        full_name = queue.pop()
        try:
            populate_dependencies(Module.get_for_full_name(full_name))
        except Module.DoesNotExist:
            raise Exception('Dependency module %s not found' % full_name)

    return dependencies
