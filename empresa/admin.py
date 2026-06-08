from django.contrib import admin

# Registerfrom django.contrib import admin
from .models import Empresa, UsuarioEmpresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'ruc',
        'telefono',
        'email',
        'plan',
        'max_usuarios',
        'estado',
    )

    search_fields = (
        'nombre',
        'ruc',
        'email'
    )

    list_filter = (
        'plan',
        'estado'
    )


@admin.register(UsuarioEmpresa)
class UsuarioEmpresaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'empresa',
        'estado',
    )

    search_fields = (
        'user__username',
        'empresa__nombre',
    )

    list_filter = (
        'empresa',
        'estado',
    )
