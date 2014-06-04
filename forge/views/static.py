from django.views.static import serve as static_serve


def serve(request, path, document_root=None, show_indexes=False):
    """
    Static file serving for Forge releases; should only be used when DEBUG
    is set -- it deletes 'Content-Encoding' header so that module tarball
    data isn't extracted twice by the Puppet module tool.
    """
    response = static_serve(request, path,
                            document_root=document_root,
                            show_indexes=show_indexes)
    if path.endswith('.tar.gz'):
        del response['Content-Encoding']
    return response
