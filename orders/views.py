from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from .permissions import IsOwnerOrAdmin
from cart.models import Cart

@extend_schema_view(
    list=extend_schema(tags=['Buyurtmalar'], summary='Buyurtmalar ro\'yxati (mijoz o\'zinikini, admin hammasini)'),
    retrieve=extend_schema(tags=['Buyurtmalar'], summary='Bitta buyurtma tafsilotini ko\'rish'),
    create=extend_schema(tags=['Buyurtmalar'], summary='Savatdagi mahsulotlardan buyurtma yaratish', request=OrderCreateSerializer, responses={201: OrderSerializer}),
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.none()
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrAdmin]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        base_queryset = Order.objects.prefetch_related('items__product').select_related('user')
        if self.request.user.is_staff:
            return base_queryset.all()
        return base_queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        cart = Cart.objects.filter(user=user).prefetch_related('items__product').first()

        if not cart or not cart.items.exists():
            return Response(
                {'detail': 'Savat bo\'sh. Buyurtma berish uchun avval mahsulot qo\'shing.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        address = serializer.validated_data.get('address') or user.address
        if not address:
            return Response(
                {'detail': 'Yetkazib berish manzili kiritilishi shart.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            cart_items = list(cart.items.select_related('product'))

            for item in cart_items:
                if item.quantity > item.product.stock:
                    return Response(
                        {
                            'detail': f'"{item.product.name}" mahsulotidan yetarli miqdor yo\'q. Ombordagi qoldiq: {item.product.stock} ta.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            total_price = sum(item.product.price * item.quantity for item in cart_items)

            order = Order.objects.create(
                user=user,
                address=address,
                total_price=total_price,
                status=Order.STATUS_PENDING
            )

            order_items = []
            for item in cart_items:
                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                )
                item.product.stock -= item.quantity
                item.product.save(update_fields=['stock'])

            OrderItem.objects.bulk_create(order_items)
            cart.items.all().delete()

        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Buyurtmalar'],
        summary='Buyurtmani bekor qilish (faqat pending holatida)',
        responses={200: OrderSerializer}
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status != Order.STATUS_PENDING:
            return Response(
                {'detail': 'Faqat kutilayotgan (pending) holatidagi buyurtmani bekor qilish mumkin.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            order.status = Order.STATUS_CANCELLED
            order.save(update_fields=['status'])

            for item in order.items.select_related('product'):
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Buyurtmalar'],
        summary='Buyurtma statusini o\'zgartirish (faqat admin)',
        request=OrderStatusUpdateSerializer,
        responses={200: OrderSerializer}
    )
    @action(detail=True, methods=['patch'], url_path='status', permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        order.status = new_status
        order.save(update_fields=['status'])

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
