from rest_framework import serializers


class WhatsAppConfigSerializer(serializers.Serializer):
    phone_number_id = serializers.CharField(max_length=50)
    business_account_id = serializers.CharField(max_length=50)
    access_token = serializers.CharField()
