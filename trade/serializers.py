from rest_framework import serializers
from .models import stocks, Buy, Sell

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = stocks
        fields = '__all__'

class BuySerializer(serializers.ModelSerializer):
    class Meta:
        model = Buy
        fields = '__all__'
    
class SellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sell
        fields = '__all__'