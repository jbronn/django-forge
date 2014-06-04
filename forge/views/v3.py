import urllib
import urlparse

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from .utils import json_response
from ..models import Author, Module, Release


def error_response(errors, **kwargs):
    """
    Returns an error response, for v3 Forge API.
    """
    error_dict = {'errors': errors}
    if 'message' in kwargs:
        error_dict['message'] = kwargs['message']
    return json_response(
        error_dict, indent=2,
        status=kwargs.get('status', 400)
    )


def pagination_data(qs, query, url_name):
    """
    Returns a two-tuple comprising a Page and dictionary of pagination data
    corresponding to the given queryset, query dictionary, and URL name.
    """
    limit = query.get('limit', 20)
    offset = query.get('offset', 0)

    p = Paginator(qs, limit)
    page_num = (offset / p.per_page) + 1
    page = p.page(page_num)

    cur_url = urlparse.urlsplit(reverse(url_name))
    first_query = query.copy()
    first_query['offset'] = 0
    first_url = urlparse.urlunsplit(
        (cur_url.scheme, cur_url.netloc, cur_url.path,
         urllib.urlencode(first_query), cur_url.fragment)
    )

    if page.has_previous():
        prev_query = query.copy()
        prev_query['offset'] = (page_num - 2) * p.per_page
        prev_url = urlparse.urlunsplit(
            (cur_url.scheme, cur_url.netloc, cur_url.path,
             urllib.urlencode(prev_query), cur_url.fragment)
        )
    else:
        prev_url = None

    if page.has_next():
        next_query = query.copy()
        next_query['offset'] = page_num * p.per_page
        next_url = urlparse.urlunsplit(
            (cur_url.scheme, cur_url.netloc, cur_url.path,
             urllib.urlencode(next_query), cur_url.fragment)
        )
    else:
        next_url = None

    pagination_dict = {
        'limit': limit,
        'offset': offset,
        'first': first_url,
        'previous': prev_url,
        'next': next_url,
        'total': p.count,
    }

    return page, pagination_dict


def modules(request):
    pass


def releases(request):
    """
    Provides the `/v3/releases` API endpoint.
    """
    qs = Release.objects.all()

    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0

    query = {
        'limit': limit,
        'offset': offset,
    }

    module_name = request.GET.get('module', None)
    if module_name:
        query['module'] = module_name
        try:
            qs = qs.filter(
                module=Module.objects.get_for_full_name(module_name)
            )
        except Module.DoesNotExist:
            qs = qs.none()

    # Get pagination page and data.
    page, pagination_dict = pagination_data(qs, query, 'releases_v3')

    releases = []
    for release in page.object_list:
        releases.append({
            'module': {
                'name': release.module.name.lower(),
                'owner': {
                    'name': release.module.author.name.lower(),
                }
            },
            'metadata': release.metadata,
            'version': str(release.version),
            'file_uri': release.tarball.url,
            'file_size': release.file_size,
            'file_md5': release.file_md5,
        })

    releases_data = {
        'pagination': pagination_dict,
        'results': releases,
    }

    return json_response(releases_data, indent=2)
