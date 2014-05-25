from django.http import HttpResponse
from django.utils import simplejson


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
