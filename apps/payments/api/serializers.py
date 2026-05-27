from rest_framework import serializers

from apps.payments.models import PaymentTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "provider",
            "amount",
            "currency",
            "status",
            "payment_url",
            "phone_number",
            "description",
            "created_at",
            "completed_at",
        ]
