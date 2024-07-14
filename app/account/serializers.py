from rest_framework import serializers

from core.models import Account


class AccountSerializer(serializers.ModelSerializer):
    '''Serializer for the account object'''
    class Meta:
        '''Meta class for the account serializer'''
        model = Account
        fields = [
            'id',
            'user',
            'type',
            'balance',
        ]
        read_only_fields = ['id', 'user', 'balance']


    def update(self, instance, validated_data):
        '''Update an account, preventing the user from changing the type'''
        validated_data.pop('type', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance