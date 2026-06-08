from django.urls import path
from . import views
# from .views import get_usuarios

urlpatterns = [    
    path('get_clientes', views.get_clientes, name='get_clientes'),    
    path('get_clientes_by_empresa_id/<int:empresa_id>', views.get_clientes_by_empresa_id, name='get_clientes_by_empresa_id'),    
    path('create_cliente', views.create_cliente, name='create_cliente'),
    path('update_cliente/<int:cliente_id>', views.update_cliente, name='update_cliente'),
    path('delete_cliente/<int:cliente_id>', views.delete_cliente, name='delete_cliente'),
]