from django.shortcuts import render


def custom_400(request, exception):
    context = {
        'title': 'Bad Request.'
    }
    return render(request, 'g_calendar/errors/400.html', context)


def custom_403(request, exception):
    context = {
        'title': 'Permission denied.'
    }
    return render(request, 'g_calendar/errors/403.html', context)


def custom_404(request, exception):
    context = {
        'title': 'Page not found.'
    }
    return render(request, 'g_calendar/errors/404.html', context)


def custom_500(request):
    context = {
        'title': 'Server error.'
    }
    return render(request, 'g_calendar/errors/500.html', context)
