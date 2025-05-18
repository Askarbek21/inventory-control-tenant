from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client 
        fields = '__all__'
    
    def validate(self, attrs):
        if attrs['type'] == 'Юр.лицо' and not attrs['ceo_name'] and not attrs['balance']:
            raise serializers.ValidationError('Имя директора и баланс не могут быть пустыми')
        return attrs
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)

        if repr['type'] == 'Физ.лицо':
            repr.pop('ceo_name')
            repr.pop('balance')

        return repr