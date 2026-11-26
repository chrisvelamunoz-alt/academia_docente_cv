from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods


@require_http_methods(["GET", "POST"])
def registro_view(request):
    """Registra una cuenta nueva con UserCreationForm y redirige a iniciar sesión."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")
    else:
        form = UserCreationForm()

    return render(request, "accounts/registro.html", {"form": form})


@never_cache
@login_required
@require_GET
def panel_view(request):
    """Muestra el panel protegido únicamente a usuarios con sesión activa."""
    return render(request, "accounts/panel.html")
