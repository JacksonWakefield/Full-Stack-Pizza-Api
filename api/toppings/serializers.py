from rest_framework import serializers
from .models import Toppings

class ToppingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Toppings
        fields = "__all__"

