from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from django.db.models import Avg
from .models import Category, Product, Review

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'product', 'user', 'username', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'product', 'user', 'username', 'created_at')

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Reyting 1 dan 5 gacha bo\'lishi kerak.')
        return value

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    avg_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'category',
            'category_name',
            'category_detail',
            'name',
            'description',
            'price',
            'stock',
            'image',
            'is_active',
            'avg_rating',
            'reviews_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'avg_rating', 'reviews_count')

    @extend_schema_field(serializers.FloatField())
    def get_avg_rating(self, obj) -> float:
        val = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(float(val), 1) if val is not None else 0.0

    @extend_schema_field(serializers.IntegerField())
    def get_reviews_count(self, obj) -> int:
        return obj.reviews.count()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Mahsulot narxi musbat son bo\'lishi kerak.')
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError('Mahsulot soni 0 dan kam bo\'lishi mumkin emas.')
        return value
