from django.shortcuts import render


def home(request):
    """Render the main portal page with navigation links."""
    return render(request, 'portal/home.html')
