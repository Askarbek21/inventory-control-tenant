from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client 
        fields = '__all__'
    
    def validate(self, attrs):
        if attrs.get('type') == 'Юр.лицо' and not attrs.get('ceo_name') and not attrs.get('balance'):
            raise serializers.ValidationError('Имя директора и баланс не могут быть пустыми')
        return attrs
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)

        if repr['type'] == 'Физ.лицо':
            repr.pop('ceo_name')
            repr.pop('balance')

        return repr
