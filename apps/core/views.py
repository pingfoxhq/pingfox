from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    """
    Render the home page of the application.
    """
    return render(request, 'core/home.html')


def test_message(request):
    """
    Render a test messagss
    """
    messages.success(request, "This is a test message!")
    messages.error(request, "This is an error message!")
    messages.info(request, "This is an info message!")
    messages.warning(request, "This is a warning message!")
    messages.debug(request, "This is a debug message!")
    return redirect('dashboard:dashboard')