# usuarios/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from empresa.models import Empresa
from empresa.models import UsuarioEmpresa  # ⭐ Importar desde empresa

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    empresas = serializers.SerializerMethodField()
    empresa_id = serializers.SerializerMethodField()
    empresa_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'is_active', 'is_staff', 'is_superuser',
            'last_login', 'date_joined', 'empresas', 'empresa_id', 'empresa_nombre'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_empresas(self, obj):
        """Obtener todas las empresas del usuario"""
        # ⭐ Sin filtro de estado
        usuario_empresas = UsuarioEmpresa.objects.filter(user=obj)
        return [
            {
                'id': ue.empresa.id,
                'nombre': ue.empresa.nombre
            }
            for ue in usuario_empresas
        ]
    
    def get_empresa_id(self, obj):
        """Obtener la primera empresa del usuario"""
        # ⭐ Sin filtro de estado
        usuario_empresa = UsuarioEmpresa.objects.filter(user=obj).first()
        return usuario_empresa.empresa.id if usuario_empresa else None
    
    def get_empresa_nombre(self, obj):
        """Obtener el nombre de la primera empresa del usuario"""
        # ⭐ Sin filtro de estado
        usuario_empresa = UsuarioEmpresa.objects.filter(user=obj).first()
        return usuario_empresa.empresa.nombre if usuario_empresa else None

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    empresa_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'password', 'is_active', 'is_staff', 'is_superuser', 'empresa_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, data):
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'username': 'Este nombre de usuario ya está en uso'}
            )
        
        email = data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Este email ya está registrado'}
            )
        
        empresa_id = data.get('empresa_id')
        if empresa_id:
            try:
                Empresa.objects.get(id=empresa_id)
            except Empresa.DoesNotExist:
                raise serializers.ValidationError(
                    {'empresa_id': 'La empresa especificada no existe'}
                )
        
        return data
    
    def create(self, validated_data):
        empresa_id = validated_data.pop('empresa_id')
        
        user = User.objects.create_user(**validated_data)
        
        try:
            empresa = Empresa.objects.get(id=empresa_id)
            # ⭐ Crear relación sin campo de estado
            UsuarioEmpresa.objects.create(
                user=user,
                empresa=empresa
            )
        except Empresa.DoesNotExist:
            pass
        
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    empresa_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'password', 'is_active', 'is_staff', 'is_superuser', 'empresa_id'
        ]
    
    def validate_username(self, value):
        instance = self.instance
        if User.objects.exclude(pk=instance.pk).filter(username=value).exists():
            raise serializers.ValidationError('Este nombre de usuario ya está en uso')
        return value
    
    def validate_email(self, value):
        instance = self.instance
        if value and User.objects.exclude(pk=instance.pk).filter(email=value).exists():
            raise serializers.ValidationError('Este email ya está registrado')
        return value
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        empresa_id = validated_data.pop('empresa_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        if empresa_id is not None:
            try:
                empresa = Empresa.objects.get(id=empresa_id)
                # ⭐ Sin campo de estado
                usuario_empresa, created = UsuarioEmpresa.objects.get_or_create(
                    user=instance,
                    empresa=empresa
                )
            except Empresa.DoesNotExist:
                pass
        
        return instance