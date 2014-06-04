import urllib
import urlparse

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from .utils import json_response
from ..models import Author, Module, Release


## Helper methods

def error_response(errors, **kwargs):
    """
    Returns an error response for v3 Forge API.
    """
    error_dict = {'errors': errors}
    if 'message' in kwargs:
        error_dict['message'] = kwargs['message']
    return json_response(
        error_dict, indent=2,
        status=kwargs.get('status', 400)
    )


def query_dict(request):
    """
    Returns query dictionary initialized with common parameters to v3 views.
    """
    try:
        limit = int(request.GET.get('limit', 20))
    except ValueError:
        limit = 20

    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0

    return {
        'limit': limit,
        'offset': offset,
    }


def pagination_data(qs, query, url_name):
    """
    Returns a two-tuple comprising a Page and dictionary of pagination data
    corresponding to the given queryset, query parameters, and URL name.
    """
    limit = query['limit']
    offset = query['offset']

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


## API views

def modules(request):
    """
    Provides the `/v3/modules` API endpoint.
    """
    query = query_dict(request)

    q = request.GET.get('query', None)
    if q:
        # Client has provided a search query..
        query['query'] = q

        parsed = Module.objects.parse_full_name(q)
        if parsed:
            # If query looks like a module name, try and get it.
            author, name = parsed
            qs = Module.objects.filter(author__name=author, name=name)
        else:
            # Otherwise we search other fields.
            qs = (
                Module.objects.filter(name__icontains=q) |
                Module.objects.filter(author__name__icontains=q) |
                Module.objects.filter(releases__version__icontains=q) |
                Module.objects.filter(tags__icontains=q) |
                Module.objects.filter(desc__icontains=q)
            )
    else:
        qs = Module.objects.all()

    # Ensure only distinct records are returned.
    qs = qs.order_by('author__name').distinct()

    # Get pagination page and data.
    page, pagination_dict = pagination_data(qs, query, 'modules_v3')

    modules_data = {
        'pagination': pagination_dict,
        'results': [module.v3 for module in page.object_list],
    }

    return json_response(modules_data, indent=2)


def releases(request):
    """
    Provides the `/v3/releases` API endpoint.
    """
    query = query_dict(request)
    qs = Release.objects.all()

    module_name = request.GET.get('module', None)
    if module_name:
        query['module'] = module_name
        if Module.objects.parse_full_name(module_name):
            try:
                qs = qs.filter(
                    module=Module.objects.get_for_full_name(module_name)
                )
            except Module.DoesNotExist:
                qs = qs.none()
        else:
            return error_response(
                ["'%s' is not a valid full modulename" % module_name]
            )

    # Get pagination page and data.
    page, pagination_dict = pagination_data(qs, query, 'releases_v3')

    # Constructing releases_data dictionary for serialization.
    releases_data = {
        'pagination': pagination_dict,
        'results': [rel.v3 for rel in page.object_list],
    }

    return json_response(releases_data, indent=2)
