from django.shortcuts import render


def home(request):
    """Render the main portal page using the Expressive template."""
    return render(request, 'expressive/index.html')
