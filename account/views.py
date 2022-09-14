from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required

from .forms import ProfileForm
from .utils import pop_session_next, account_entrypoint

# Create your views here.

@account_entrypoint()
def home(request):
    if not request.user.is_authenticated:
        return redirect(reverse("account:login"))
    return render(request, 'account/home.html')

def leave(request):
    nexturl = pop_session_next(request)
    return redirect(nexturl)

@login_required(login_url=reverse_lazy('account:home'))
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            nexturl = request.GET.get("next", "")
            if nexturl:
                return redirect(reverse('account:home')+"?next="+nexturl)
            return redirect(reverse('account:home'))
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'account/profile.html', {'form': form})

def error404(request):
    return render(request, 'account/error.html', status=404)
