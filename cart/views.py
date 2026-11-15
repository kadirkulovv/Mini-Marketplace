from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, RemoveFromCartSerializer
from products.models import Product

class CartViewSet(viewsets.GenericViewSet):
    queryset = Cart.objects.none()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_cart(self, user):
        cart, _ = Cart.objects.prefetch_related('items__product').get_or_create(user=user)
        return cart

    @extend_schema(
        tags=['Savat'],
        summary='Foydalanuvchining shaxsiy savatini ko\'rish',
        responses={200: CartSerializer}
    )
    def list(self, request):
        cart = self.get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        tags=['Savat'],
        summary='Savatga mahsulot qo\'shish',
        request=AddToCartSerializer,
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request):
        serializer = AddToCartSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        cart = self.get_cart(request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        updated_cart = self.get_cart(request.user)
        return Response(CartSerializer(updated_cart).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Savat'],
        summary='Savatdan mahsulotni ayirish yoki o\'chirish',
        request=RemoveFromCartSerializer,
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['post'], url_path='remove')
    def remove(self, request):
        serializer = RemoveFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)
        cart = self.get_cart(request.user)

        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Mahsulot savatda mavjud emas.'}, status=status.HTTP_404_NOT_FOUND)

        if cart_item.quantity > quantity:
            cart_item.quantity -= quantity
            cart_item.save()
        else:
            cart_item.delete()

        updated_cart = self.get_cart(request.user)
        return Response(CartSerializer(updated_cart).data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Savat'],
        summary='Savatni to\'liq tozalash',
        responses={200: CartSerializer}
    )
    @action(detail=False, methods=['post'], url_path='clear')
    def clear(self, request):
        cart = self.get_cart(request.user)
        cart.items.all().delete()
        updated_cart = self.get_cart(request.user)
        return Response(CartSerializer(updated_cart).data, status=status.HTTP_200_OK)
