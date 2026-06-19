# usuarios/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q
from .serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer
from empresa.models import UsuarioEmpresa  # ⭐ Importar desde empresa
from empresa.models import Empresa
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='all-users')
    def all_users(self, request):
        """
        Endpoint para que el superadministrador obtenga TODOS los usuarios
        sin filtro de empresa.
        """
        user = request.user
        
        # Verificar que sea superadministrador
        if not user.is_superuser:
            return Response(
                {'error': 'No tienes permiso para acceder a todos los usuarios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener todos los usuarios
        queryset = User.objects.all().order_by('-date_joined')
        
        # Aplicar filtros opcionales
        search = self.request.query_params.get('search', '')
        is_active = self.request.query_params.get('is_active')
        is_staff = self.request.query_params.get('is_staff')
        is_superuser = self.request.query_params.get('is_superuser')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if is_active is not None:
            if is_active.lower() == 'true':
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == 'false':
                queryset = queryset.filter(is_active=False)
        
        if is_staff is not None:
            if is_staff.lower() == 'true':
                queryset = queryset.filter(is_staff=True)
            elif is_staff.lower() == 'false':
                queryset = queryset.filter(is_staff=False)
        
        if is_superuser is not None:
            if is_superuser.lower() == 'true':
                queryset = queryset.filter(is_superuser=True)
            elif is_superuser.lower() == 'false':
                queryset = queryset.filter(is_superuser=False)
        
        # Paginación (opcional)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        
        if user.is_superuser:
            queryset = super().get_queryset()
        else:
            # ⭐ Sin filtro de estado
            empresas_ids = UsuarioEmpresa.objects.filter(
                user=user
            ).values_list('empresa_id', flat=True)
            
            usuarios_ids = UsuarioEmpresa.objects.filter(
                empresa_id__in=empresas_ids
            ).values_list('user_id', flat=True)
            
            queryset = User.objects.filter(id__in=usuarios_ids)
        
        # Filtros
        search = self.request.query_params.get('search', '')
        is_active = self.request.query_params.get('is_active')
        is_staff = self.request.query_params.get('is_staff')
        is_superuser = self.request.query_params.get('is_superuser')
        empresa_id = self.request.query_params.get('empresa_id')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if is_active is not None:
            if is_active.lower() == 'true':
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == 'false':
                queryset = queryset.filter(is_active=False)
        
        if is_staff is not None:
            if is_staff.lower() == 'true':
                queryset = queryset.filter(is_staff=True)
            elif is_staff.lower() == 'false':
                queryset = queryset.filter(is_staff=False)
        
        if is_superuser is not None:
            if is_superuser.lower() == 'true':
                queryset = queryset.filter(is_superuser=True)
            elif is_superuser.lower() == 'false':
                queryset = queryset.filter(is_superuser=False)
        
        if empresa_id and user.is_superuser:
            try:
                empresa_id = int(empresa_id)
                # ⭐ Sin filtro de estado
                usuarios_ids = UsuarioEmpresa.objects.filter(
                    empresa_id=empresa_id
                ).values_list('user_id', flat=True)
                queryset = queryset.filter(id__in=usuarios_ids)
            except ValueError:
                pass
        
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user
        
        if not user.is_superuser:
            # ⭐ Sin filtro de estado
            usuario_empresa = UsuarioEmpresa.objects.filter(
                user=user
            ).first()
            
            if not usuario_empresa:
                return Response(
                    {'error': 'El usuario no tiene una empresa asignada'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            request.data['empresa_id'] = usuario_empresa.empresa_id
        
        try:
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            new_user = serializer.save()
            
            return Response(
                UserSerializer(new_user).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"❌ Error al crear usuario: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='crear-con-empresa')
    def crear_con_empresa(self, request):
        """
        Crear un usuario y asignarlo a una empresa con rol específico
        Este método maneja la creación de usuarios con es_admin_empresa
        """
        try:
            data = request.data
            
            # Validar que el usuario actual tenga permisos
            current_user = request.user
            
            # Validar datos requeridos
            required_fields = ['username', 'email', 'first_name', 'last_name', 'password', 'empresa_id']
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {field: f'El campo {field} es requerido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Si no es superadmin, verificar permisos
            if not current_user.is_superuser:
                # Verificar que el usuario actual sea admin de la empresa
                usuario_empresa = UsuarioEmpresa.objects.filter(
                    user=current_user,
                    empresa_id=data['empresa_id']
                ).first()
                
                if not usuario_empresa or not usuario_empresa.es_admin_empresa:
                    return Response(
                        {'error': 'No tienes permiso para crear usuarios en esta empresa'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Si no es superadmin, no puede crear otros admins
                if data.get('es_admin_empresa', False):
                    return Response(
                        {'error': 'No tienes permiso para crear administradores de empresa'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Validar que la empresa existe
            try:
                empresa = Empresa.objects.get(id=data['empresa_id'])
            except Empresa.DoesNotExist:
                return Response(
                    {'error': 'La empresa especificada no existe'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validar que el username no exista
            if User.objects.filter(username=data['username']).exists():
                return Response(
                    {'username': 'Este nombre de usuario ya está en uso'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar que el email no exista
            if data.get('email') and User.objects.filter(email=data['email']).exists():
                return Response(
                    {'email': 'Este email ya está registrado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear usuario con transacción
            with transaction.atomic():
                # Crear usuario
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    password=data['password'],
                    is_active=data.get('is_active', True),
                    is_staff=False,  # Forzamos a False para evitar acceso al admin de Django
                    is_superuser=False  # Forzamos a False, solo el superadmin existe
                )
                
                # Crear relación usuario-empresa
                UsuarioEmpresa.objects.create(
                    user=user,
                    empresa=empresa,
                    es_admin_empresa=data.get('es_admin_empresa', False)
                )
            
            # Serializar respuesta
            response_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'empresa_id': empresa.id,
                'empresa_nombre': empresa.nombre,
                'es_admin_empresa': data.get('es_admin_empresa', False)
            }
            
            logger.info(f"✅ Usuario {user.username} creado exitosamente en empresa {empresa.nombre}")
            
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"❌ Error al crear usuario: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )            

    @action(detail=False, methods=['get'])
    def mis_empresas(self, request):
        user = request.user
        # ⭐ Sin filtro de estado
        usuario_empresas = UsuarioEmpresa.objects.filter(
            user=user
        ).select_related('empresa')
        
        empresas = [
            {
                'id': ue.empresa.id,
                'nombre': ue.empresa.nombre
            }
            for ue in usuario_empresas
        ]
        
        return Response(empresas)

    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        is_active = request.data.get('is_active')
        
        if is_active is None:
            return Response(
                {'error': 'El campo is_active es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = is_active
        user.save()
        
        return Response(
            {'message': f'Usuario {"activado" if is_active else "desactivado"} correctamente'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get('password')
        
        if not new_password:
            return Response(
                {'error': 'La contraseña es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth.password_validation import validate_password
            validate_password(new_password, user)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'message': 'Contraseña actualizada correctamente'},
            status=status.HTTP_200_OK
        )