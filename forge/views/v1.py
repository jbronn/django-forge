from django.shortcuts import render

from .json import error_response, json_response
from ..dependency import module_dependencies
from ..models import Module, Release


def module_dict(module):
    """
    Helper method to return a dictionary (for JSON generation) for the
    given module.
    """
    latest = module.latest_release
    versions = [release.version for release in module.releases.all()]
    versions.sort(reverse=True)
    metadata = latest.metadata
    return {
        'name': module.name,
        'author': module.author.name,
        'version': str(latest.version),
        'full_name': str(module),
        'desc': module.desc,
        'project_url': metadata.get('project_page', ''),
        'releases': [{'version': str(version)} for version in versions],
        'tag_list': module.tag_list,
    }


def module_json(request, author, module_name):
    """
    Provides the `<author>/<module>.json` URL.

    This hidden API is used by third parties, such as Puppet Librarian.
    """
    full_name = '%s/%s' % (author, module_name)
    try:
        module = Module.objects.get(author__name=author, name=module_name)
    except Module.DoesNotExist:
        return error_response('Module %s not found' % full_name, status=410)
    return json_response(module_dict(module))


def modules_json(request):
    """
    Provides the `/modules.json` URL expected by `puppet module`.
    """
    query = request.GET.get('q', None)

    if query:
        # Client has provided a search query..
        parsed = Module.parse_full_name(query)
        if parsed:
            # If query looks like a module name, try and get it.
            author, name = parsed
            module_qs = Module.objects.filter(author__name=author,
                                              name=name)
        else:
            # Otherwise we search other fields.
            module_qs = (
                Module.objects.filter(name__icontains=query) |
                Module.objects.filter(author__name__icontains=query) |
                Module.objects.filter(releases__version__icontains=query) |
                Module.objects.filter(tags__icontains=query) |
                Module.objects.filter(desc__icontains=query)
            )
    else:
        # No query provided, use all modules.
        module_qs = Module.objects.all()

    modules = []
    for module in module_qs.order_by('author__name').distinct():
        modules.append(module_dict(module))
    return json_response(modules)


def releases_json(request):
    """
    Provides the `/api/v1/releases.json` URL expected by `puppet module`.
    """
    full_name = request.GET.get('module', None)
    if not full_name:
        return error_response(['Parameter module is required'])

    parsed = Module.parse_full_name(full_name)
    if not parsed:
        return error_response(['Invalid module name'])

    try:
        module = Module.get_for_full_name(full_name)
    except Module.DoesNotExist:
        return error_response('Module %s not found' % full_name, status=410)

    version = request.GET.get('version', None)
    if version:
        try:
            release = Release.objects.get(module=module, version=version)
        except Release.DoesNotExist:
            return error_response('Module %s has no release for version %s' %
                                  (full_name, version), status=410)
    else:
        release = None

    try:
        return json_response(module_dependencies(module, release))
    except Exception as e:
        return error_response([e.message], status=410)