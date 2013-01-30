from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import simplejson

from .models import Author, Module, Release


def json_response(data, indent=None, status=None):
    return HttpResponse(simplejson.dumps(data, indent=indent),
                        mimetype='application/json',
                        status=status)


def error_response(errors, **kwargs):
    kwargs.setdefault('status', 400)
    # The Puppet Forge sometimes returns it's errors in one of two ways,
    # as a list:
    #   {"errors": [ "<msg1>" ... "<msgN>" ]}
    # Or as a single element:
    #   {"error": "<msg>"}
    if isinstance(errors, (list, tuple)):
        key = 'errors'
    else:
        key = 'error'
    return json_response({key: errors}, **kwargs)


def handler404(request):
    return render(request, 'admin/404.html', {})


def handler500(request):
    return render(request, 'admin/500.html', {})


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
                Module.objects.filter(release__version__icontains=query) |
                Module.objects.filter(tags__icontains=query) |
                Module.objects.filter(desc__icontains=query)
            )
    else:
        # No query provided, use all modules.
        module_qs = Module.objects.all()

    modules = []
    for module in module_qs.order_by('author__name').distinct():
        # TODO: Store dates in database, don't rely on primary key order.
        releases = Release.objects.filter(module=module).order_by('-pk')
        latest = releases[0]
        metadata = latest.metadata
        modules.append({
            'name': module.name,
            'author': module.author.name,
            'version': latest.version,
            'full_name': str(module),
            'desc': metadata.get('summary', ''),
            'project_url': metadata.get('project_page', ''),
            'releases': [{'version': release.version}
                         for release in releases],
            'tag_list': module.tag_list,
        })
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
            mod_release = Release.objects.get(module=module, version=version)
        except Release.DoesNotExist:
            return error_response('Module %s has no release for version %s' %
                                  (full_name, version), status=410)
    else:
        mod_release = None

    # This is the code that figures out dependencies; there is much
    # room for improvement.
    dependencies = {}
    queue = set()
    def populate_dependencies(mod, release=None):
        if release is None:
            release = Release.objects.filter(module=mod).order_by('-pk')[0]

        release_dependencies = [
            (depend['name'], depend['version_requirement'])
            for depend in release.metadata.get('dependencies', [])
        ]
        full_name = str(release.module)
        release_info = {
            'version': release.version,
            'file': release.tarball.url,
            'dependencies': release_dependencies,
        }

        if dependencies.get(full_name, None):
            dependencies[full_name].append(release_info)
        else:
            dependencies[full_name] = [release_info]

        for name, version in release_dependencies:
            if not name in dependencies:
                queue.add(name)

    # Keep going until we don't have any dependencies left.
    populate_dependencies(module, mod_release)
    while queue:
        full_name = queue.pop()
        try:
            populate_dependencies(Module.get_for_full_name(full_name))
        except Module.DoesNotExist:
            err = 'Dependency module %s not found' % full_name
            return error_response([err], status=410)

    return json_response(dependencies)