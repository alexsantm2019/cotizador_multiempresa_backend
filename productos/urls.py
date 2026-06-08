from django.urls import path
from . import views
# from .views import get_usuarios

urlpatterns = [    
    path('get_productos', views.get_productos, name='get_productos'),    
    path('get_productos_by_empresa_id/<int:empresa_id>', views.get_productos_by_empresa_id, name='get_productos_by_empresa_id'),    
    path('get_productos_inventario', views.get_productos_inventario, name='get_productos_inventario'),    
    path('get_productos_inventario_by_empresa_id/<int:empresa_id>', views.get_productos_inventario_by_empresa_id, name='get_productos_inventario_by_empresa_id'),    
    path('create_producto', views.create_producto, name='create_producto'),
    path('update_producto/<int:producto_id>', views.update_producto, name='update_producto'),
    path('delete_producto/<int:producto_id>', views.delete_producto, name='delete_producto'),
    path('update_inventario/<int:producto_id>', views.update_inventario, name='update_inventario'),
]