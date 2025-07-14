from django.shortcuts import render, redirect
from .forms import SiteCreationForm
from django.contrib.auth.decorators import login_required
from .models import Site
from django.contrib import messages

@login_required
def create_site(request):
    form = SiteCreationForm(request.POST or None, initial={"user": request.user})
    if request.method == "POST" and form.is_valid():
        site: Site = form.save(commit=False)
        site.user = request.user
        site.save()
        messages.success(request, "Site created successfully!")
        return redirect("dashboard:index")
    return render(request, "sites/create.html", {"form": form})