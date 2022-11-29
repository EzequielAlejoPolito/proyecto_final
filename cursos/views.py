from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from cursos.forms import Comentarios
from cursos.forms import EstructuraCurso
from cursos.forms import EstructuraEjercicios
from cursos.models import Comentario
from cursos.models import Cursos
from cursos.models import Ejercicios

class ListaCurso(ListView):
    model = Cursos
    paginate_by = 3

class InfoCurso(DetailView):
    model = Cursos
    template_name = "cursos/curso_info.html"
    fields = ["name", "code", "description"]

    def get(self, request, pk):
        course = Cursos.objects.get(id=pk)
        comments = Comentario.objects.filter(course=course).order_by("-updated_at")
        comment_form = Comentarios()
        context = {
            "course": course,
            "comments": comments,
            "comment_form": comment_form,
        }
        return render(request, self.template_name, context)


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Cursos
    success_url = reverse_lazy("course:homework-list")

    form_class = EstructuraCurso
    # fields = ["name", "code", "description", "image"]

    def form_valid(self, form):
        
        data = form.cleaned_data
        form.instance.owner = self.request.user
        actual_objects = Cursos.objects.filter(
            name=data["name"], code=data["code"]
        ).count()
        if actual_objects:
            messages.error(
                self.request,
                f"El curso {data['name']} - {data['code']} ya está creado",
            )
            form.add_error("name", ValidationError("Acción no válida"))
            return super().form_invalid(form)
        else:
            messages.success(
                self.request,
                f"Curso {data['name']} - {data['code']} creado exitosamente!",
            )
            return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Cursos
    fields = ["name", "code", "description", "image"]

    def get_success_url(self):
        course_id = self.kwargs["pk"]
        return reverse_lazy("course:curso-info", kwargs={"pk": course_id})


class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = Cursos
    success_url = reverse_lazy("course:course-list")


class CommentCreateView(LoginRequiredMixin, CreateView):
    def post(self, request, pk):
        course = get_object_or_404(Cursos, id=pk)
        comment = Comentario(
            text=request.POST["comment_text"], owner=request.user, course=course
        )
        comment.save()
        return redirect(reverse("course:course-detail", kwargs={"pk": pk}))


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comentario

    def get_success_url(self):
        course = self.object.course
        return reverse("course:course-detail", kwargs={"pk": course.id})


class HomeworkListView(ListView):
    model = Ejercicios
    paginate_by = 4


class HomeworkCreateView(LoginRequiredMixin, CreateView):
    model = Ejercicios
    success_url = reverse_lazy("course:homework-list")

    form_class = EstructuraEjercicios

    def form_valid(self, form):
        
        data = form.cleaned_data
        actual_objects = Ejercicios.objects.filter(name=data["name"]).count()
        if actual_objects:
            messages.error(
                self.request,
                f"El trabajo {data['name']} ya está creado",
            )
            form.add_error("name", ValidationError("Acción no válida"))
            return super().form_invalid(form)
        else:
            messages.success(
                self.request,
                f"Trabajo: {data['name']}. Creado exitosamente!",
            )
            return super().form_valid(form)


class HomeworkDetailView(DetailView):
    model = Ejercicios
    fields = ["name", "due_date", "is_delivered"]


class HomeworkUpdateView(LoginRequiredMixin, UpdateView):
    model = Ejercicios
    fields = ["name", "due_date", "is_delivered"]

    def get_success_url(self):
        homework_id = self.kwargs["pk"]
        return reverse_lazy("course:homework-detail", kwargs={"pk": homework_id})

class HomeworkDeleteView(LoginRequiredMixin, DeleteView):
    model = Ejercicios
    success_url = reverse_lazy("course:homework-list")