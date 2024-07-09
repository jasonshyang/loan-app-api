from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import MoneyRequest
from moneyrequest import serializers

# Create your views here.
class MoneyRequestViewSet(viewsets.ModelViewSet):
    '''Manage money requests in the database'''
    serializer_class = serializers.MoneyRequestDetailSerializer
    queryset = MoneyRequest.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''Return objects for the current authenticated user only'''
        return self.queryset.filter(borrower=self.request.user).order_by('-id')

    def get_serializer_class(self):
        '''Return appropriate serializer class'''

        if self.action == 'list':
            return serializers.MoneyRequestSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        '''Create a new money request'''
        serializer.save(borrower=self.request.user)