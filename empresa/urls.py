from django.urls import path
from .views import (
    EmpresaListCreateView,
    EmpresaDetailView,
    listar_todas_empresas
)

urlpatterns = [
    path(
        '',
        EmpresaListCreateView.as_view(),
        name='empresa-list-create'
    ),

    path(
        '<int:pk>/',
        EmpresaDetailView.as_view(),
        name='empresa-detail'
    ),
    path('lista-empresas/', listar_todas_empresas, name='lista-empresas'),
]