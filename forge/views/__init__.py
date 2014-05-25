from django.shortcuts import render


def handler404(request):
    return render(request, 'admin/404.html', {})


def handler500(request):
    return render(request, 'admin/500.html', {})
