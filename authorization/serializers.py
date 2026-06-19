from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from empresa.models import UsuarioEmpresa
from django.conf import settings
from django.utils import timezone

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        # Login JWT normal
        data = super().validate(attrs)

        # ======================================
        # DATOS DEL USUARIO
        # ======================================
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['email'] = self.user.email

        self.user.last_login = timezone.now()
        self.user.save(update_fields=['last_login'])

        if self.user.first_name and self.user.last_name:
            full_name = (
                f"{self.user.first_name} "
                f"{self.user.last_name}"
            )
        else:
            full_name = self.user.first_name

        data['full_name'] = full_name

        # ======================================
        # EMPRESA DEL USUARIO
        # ======================================
        try:
            usuario_empresa = UsuarioEmpresa.objects.select_related(
                'empresa'
            ).get(user=self.user)

            empresa = usuario_empresa.empresa

            data['empresa_id'] = (
                usuario_empresa.empresa.id
            )

            data['empresa_nombre'] = (
                usuario_empresa.empresa.nombre
            )

            data['empresa_plan'] = (
                usuario_empresa.empresa.plan
            )
             # ===============================
            # LOGO EMPRESA
            # ===============================
            if empresa.logo:
                data['empresa_logo'] = (
                    settings.MEDIA_URL +
                    str(empresa.logo)
                )
            else:
                data['empresa_logo'] = None

        except UsuarioEmpresa.DoesNotExist:
            data['empresa_id'] = None
            data['empresa_nombre'] = None
            data['empresa_plan'] = None

        return data

# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         # Llama al método validate del padre para obtener los tokens
#         data = super().validate(attrs)
        
#         # Se añaden mas datos a la api de respuesta
#         data['user_id'] = self.user.id
#         data['username'] = self.user.username
#         data['first_name'] = self.user.first_name
#         data['last_name'] = self.user.last_name
#         data['email'] = self.user.email

#         if self.user.first_name and self.user.last_name:
#             full_name = f"{self.user.first_name} {self.user.last_name}"        
#         else:
#             full_name = self.user.first_name  

#         data['full_name'] = full_name
        
#         return data

