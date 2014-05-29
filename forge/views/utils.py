import json

from django.http import HttpResponse


def json_response(data, indent=None, status=None):
    return HttpResponse(json.dumps(data, indent=indent),
                        content_type='application/json',
                        status=status)
