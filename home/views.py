import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.shortcuts import render

from cursos.models import Cursos
from home.forms import FormaUsuario
from home.forms import RegistrarUsario
from home.forms import UsuarioRegistrado
from home.models import Usuario


def get_avatar_url_ctx(request):
    avatars = Usuario.objects.filter(user=request.user.id)
    if avatars.exists():
        return {"avatar_url": avatars[0].image.url}
    return {}


def index(request):
    return render(
        request=request,
        context=get_avatar_url_ctx(request),
        template_name="home/index.html",
    )


def search(request):
    search_param = request.GET["search_param"]
    print("search: ", search_param)
    context_dict = dict()
    if search_param:
        query = Q(name__contains=search_param)
        query.add(Q(code__contains=search_param), Q.OR)
        courses = Cursos.objects.filter(query)
        context_dict.update(
            {
                "courses": courses,
                "search_param": search_param,
            }
        )
    return render(
        request=request,
        context=context_dict,
        template_name="home/index.html",
    )

def register(request):
    form = RegistrarUsario(request.POST) if request.POST else RegistrarUsario()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado exitosamente!")
            return redirect("login")

    return render(
        request=request,
        context={"form": form},
        template_name="registration/register.html",
    )


@login_required
def user_update(request):
    user = request.user
    if request.method == "POST":
        form = UsuarioRegistrado(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("home:index")

    form = UsuarioRegistrado(model_to_dict(user))
    return render(
        request=request,
        context={"form": form},
        template_name="registration/user_form.html",
    )


@login_required
def avatar_load(request):
    if request.method == "POST":
        form = FormaUsuario(request.POST, request.FILES)
        if form.is_valid and len(request.FILES) != 0:
            image = request.FILES["image"]
            avatars = Usuario.objects.filter(user=request.user.id)
            if not avatars.exists():
                avatar = Usuario(user=request.user, image=image)
            else:
                avatar = avatars[0]
                if len(avatar.image) > 0:
                    os.remove(avatar.image.path)
                avatar.image = image
            avatar.save()
            messages.success(request, "Imagen cargada exitosamente")
            return redirect("home:index")

    form = FormaUsuario()
    return render(
        request=request,
        context={"form": form},
        template_name="home/avatar_form.html",
    )