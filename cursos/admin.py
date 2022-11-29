from django.contrib import admin

from cursos.models import Cursos, Ejercicios


admin.site.register(Cursos)

admin.site.register(Ejercicios)