from django.shortcuts import render

# Create yourfrom django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Empresa
from .serializers import EmpresaSerializer


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

        empresa.deleted_at = timezone.now()
        empresa.save()

        return Response({
            'message': 'Empresa eliminada'
        })
