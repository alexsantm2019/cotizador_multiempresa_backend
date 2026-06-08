from django.urls import path
from . import views
# from .views import get_usuarios

urlpatterns = [    
    path('get_categoria_producto', views.get_categoria_producto, name='get_categoria_producto'),        
    path('get_categoria_producto_by_empresa_id/<int:empresa_id>', views.get_categoria_producto_by_empresa_id, name='get_categoria_producto_by_empresa_id'),        
    path('create_categoria_producto', views.create_categoria_producto, name='create_categoria_producto'),
    path('update_categoria_producto/<int:categoria_id>', views.update_categoria_producto, name='update_categoria_producto'),
    path('delete_categoria_producto/<int:categoria_id>', views.delete_categoria_producto, name='delete_categoria_producto'),
]