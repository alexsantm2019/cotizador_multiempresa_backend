# empresa/views.py
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# ⭐ IMPORTAR api_view y permission_classes
from rest_framework.decorators import api_view, permission_classes
# ⭐ IMPORTAR los permisos
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Empresa
from .serializers import EmpresaSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def listar_todas_empresas(request):
    """
    Endpoint exclusivo para superadmin/administradores.
    Devuelve todas las empresas sin ningún filtro.
    """
    try:
        empresas = Empresa.objects.all().order_by('nombre')
        serializer = EmpresaSerializer(empresas, many=True)
        
        logger.info(f"📊 Total empresas devueltas: {empresas.count()}")
        
        return Response({
            'success': True,
            'count': empresas.count(),
            'data': serializer.data
        })
    except Exception as e:
        logger.error(f"❌ Error al listar empresas: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=500
        )


# ==========================================
# LISTAR / CREAR
# ==========================================
class EmpresaListCreateView(APIView):

    def get(self, request):
        empresas = Empresa.objects.filter(
            deleted_at__isnull=True
        ).order_by('nombre')

        serializer = EmpresaSerializer(
            empresas,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = EmpresaSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# ==========================================
# DETALLE / EDITAR / ELIMINAR
# ==========================================
class EmpresaDetailView(APIView):

    def get_object(self, pk):
        try:
            return Empresa.objects.get(
                pk=pk,
                deleted_at__isnull=True
            )
        except Empresa.DoesNotExist:
            return None

    def get(self, request, pk):
        empresa = self.get_object(pk)

        if not empresa:
            return Response(
                {'error': 'Empresa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmpresaSerializer(
            empresa
        )

        return Response(serializer.data)

    def put(self, request, pk):
        empresa = self.get_object(pk)

        if not empresa:
            return Response(
                {'error': 'Empresa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EmpresaSerializer(
            empresa,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        empresa = self.get_object(pk)

        if not empresa:
            return Response(
                {'error': 'Empresa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        if empresa.logo:
            try:
                if os.path.isfile(empresa.logo.path):
                    os.remove(empresa.logo.path)
            except:
                pass            

        empresa.deleted_at = timezone.now()
        empresa.save()

        return Response({
            'message': 'Empresa eliminada'
        })
