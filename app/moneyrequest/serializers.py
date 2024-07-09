from rest_framework import serializers

from core.models import MoneyRequest


class MoneyRequestSerializer(serializers.ModelSerializer):
    '''Serializer for the money request object'''
    class Meta:
        '''Meta class for the money request serializer'''
        model = MoneyRequest
        fields = [
            'id',
            'title',
            'amount',
            'frequency',
            'term'
        ]
        read_only_fields = ['id']


class MoneyRequestDetailSerializer(MoneyRequestSerializer):
    '''Serializer for the money request detail object'''
    class Meta(MoneyRequestSerializer.Meta):
        '''Meta class for the money request detail serializer'''
        fields = MoneyRequestSerializer.Meta.fields + ['borrower', 'lender', 'description']
        read_only_fields = MoneyRequestSerializer.Meta.read_only_fields + ['borrower', 'lender']