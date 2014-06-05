import logging
from collections import defaultdict

from .models import Module, Release
from .semver import ForgeSpec


logger = logging.getLogger('forge.dependency')

def release_specs(release):
    """
    For the given release, return a list of all the dependencies as 2-tuples,
    comprising the module name and dependency specification as given in the
    release's metadata.
    """
    return [
        (depend['name'],
         depend.get('version_requirement', '>= 0.0.0'))
        for depend in release.metadata.get('dependencies', [])
    ]


def calculate_dependencies(release):
    """
    This function does the heavy lifting of calculating dependencies for the
    given Release instance.  It returns two data structures:

     * A dictionary of dependencies, mapping the legacy name of a module
       the release depends on (e.g., 'puppetlabs/apache') to a set of
       version specifications (e.g., '>= 1.0.0') as ForgeSpec objects.
     * A cache dictionary mapping a release's primary key it's string
       version requirements as expressed in its metadata (in other words,
       what's returned by `release_specs()` for each release.
    """
    # Prime the queue with the given release.
    queue = set([release])

    # Add the given release to the dependency structure, and lock it's
    # version specification at the version of the release.  Use the
    # legacy module name, as that what the Forge uses in its metadata
    # to express dependencies.
    dependencies = defaultdict(set)
    dependencies[release.module.legacy_name].add(
        ForgeSpec(str(release.version))
    )

    # Create dictionary for mapping of releases to their list of dependency
    # specifications.
    spec_cache = {}

    while queue:
        # Pop the next release from the queue, and get it's dependency
        # specifications (caching them for later use).
        rel = queue.pop()
        if not rel.pk in spec_cache:
            spec_cache[rel.pk] = release_specs(rel)

        for dep_item in spec_cache[rel.pk]:
            # Pull out the legacy module name, and create a `ForgeSpec`
            # object from the metadata string.
            dep_name, dep_spec = dep_item
            dep_spec = ForgeSpec(dep_spec)

            # When the specification is not in our datastructure yet,
            # get the corresponding Module, and all Releases that conform
            # to the specification and add them to the queue.
            if not dep_spec in dependencies[dep_name]:
                try:
                    dep_mod = Module.objects.get_for_full_name(dep_name)
                except Module.DoesNotExist:
                    raise Exception('Dependency module %s not found' %
                                    dep_name)

                dependencies[dep_name].add(dep_spec)
                for dep_rel in dep_mod.releases.all():
                    if dep_rel.version in dep_spec:
                        queue.add(dep_rel)

    return dependencies, spec_cache


def release_dependencies(release):
    """
    This determines the dependencies for the given module release.
    """
    logger.info('Calculating dependencies for %s' % release)
    dependency_specs, spec_cache = calculate_dependencies(release)
    dependencies = defaultdict(list)

    for dep_name, specs in dependency_specs.iteritems():
        try:
            dep_mod = Module.objects.get_for_full_name(dep_name)
        except Module.DoesNotExist:
            raise Exception('Dependency module %s not found' % dep_name)

        releases = []
        for rel in dep_mod.releases.all():
            if all([rel.version in spec for spec in specs]):
                dependencies[dep_name].append({
                        'version': str(rel.version),
                        'file': rel.tarball.url,
                        'dependencies': spec_cache[rel.pk],
                })

    return dependencies
