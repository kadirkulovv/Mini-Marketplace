from decimal import Decimal
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Cart, CartItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=12, decimal_places=2, read_only=True)
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'item_total')
        read_only_fields = ('id', 'product_name', 'product_price', 'item_total')

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_item_total(self, obj) -> Decimal:
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_items', 'total_price', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total_price(self, obj) -> Decimal:
        return sum((item.product.price * item.quantity for item in obj.items.all()), Decimal('0.00'))

    @extend_schema_field(serializers.IntegerField())
    def get_total_items(self, obj) -> int:
        return sum((item.quantity for item in obj.items.all()), 0)

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': 'Bunday mahsulot topilmadi.'})

        if not product.is_active:
            raise serializers.ValidationError({'product_id': 'Ushbu mahsulot hozirda nofaol.'})

        user = self.context['request'].user
        cart, _ = Cart.objects.get_or_create(user=user)
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        current_quantity = cart_item.quantity if cart_item else 0

        if current_quantity + quantity > product.stock:
            raise serializers.ValidationError({
                'quantity': f'Omborda yetarli mahsulot yo\'q. Mavjud qoldiq: {product.stock} ta.'
            })

        attrs['product'] = product
        return attrs

class RemoveFromCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(required=False, default=1, min_value=1)
