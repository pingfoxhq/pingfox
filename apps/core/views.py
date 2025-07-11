from django.shortcuts import render

def home(request):
    """
    Render the home page of the application.
    """
    return render(request, 'core/home.html')