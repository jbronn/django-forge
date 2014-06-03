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


def paginated_response():
    pass

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

    p = Paginator(qs, limit)
    page_num = (offset / p.per_page) + 1
    page = p.page(page_num)

    cur_url = urlparse.urlsplit(reverse('releases_v3'))
    first_query = query.copy()
    first_query['offset'] = 0
    first_url = urlparse.urlunsplit(
        (cur_url.scheme, cur_url.netloc, cur_url.path,
         urllib.urlencode(first_query), cur_url.fragment)
    )

    if page.has_previous():
        prev_query = query.copy()
        prev_query['offset'] = page_num * (p.per_page - 1)
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

    releases_data = {
        'pagination': {
            'limit': limit,
            'offset': offset,
            'first': first_url,
            'previous': prev_url,
            'next': next_url,
            'total': p.count,
        },
        'results': [
        ]
    }

    return json_response(releases_data, indent=2)
