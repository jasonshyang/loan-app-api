from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED

from core.models import Account
from account import serializers

# Create your views here.
class AccountViewSet(viewsets.ModelViewSet):
    '''Manage accounts in the database'''
    serializer_class = serializers.AccountSerializer
    queryset = Account.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        '''Return accounts for the current authenticated user only'''
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        '''Create a new account'''
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return Response(status=HTTP_405_METHOD_NOT_ALLOWED, data={'detail': 'Method "DELETE" not allowed.'})