from django.contrib.auth.models import User
from django.db import models

class Usuario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='imagen_usuario', null=True, blank=True)

    def __str__(self):
        return f'user: {self.user.username} | url: {self.image.url}'
