from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Empresa(models.Model):
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    )

    nombre = models.CharField(
        max_length=100
    )

    ruc = models.CharField(
        max_length=13,
        blank=True,
        null=True
    )

    direccion = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True
    )

    logo = models.ImageField(
        upload_to='empresas/logos/',
        blank=True,
        null=True
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='basic',
        blank=True,
        null=True
    )

    max_usuarios = models.IntegerField(
        default=5,
        blank=True,
        null=True
    )

    estado = models.BooleanField(
        default=True
    )

    deleted_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre


class UsuarioEmpresa(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='usuario_empresa'
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='usuarios'
    )

    estado = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'usuario_empresa'

    def __str__(self):
        return f'{self.user.username} - {self.empresa.nombre}'