from rest_framework import generics, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly

@extend_schema_view(
    get=extend_schema(tags=['Kategoriyalar'], summary='Barcha kategoriyalar ro\'yxati'),
    post=extend_schema(tags=['Kategoriyalar'], summary='Yangi kategoriya yaratish (faqat admin)')
)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None

@extend_schema_view(
    get=extend_schema(tags=['Kategoriyalar'], summary='Bitta kategoriya tafsilotini olish'),
    put=extend_schema(tags=['Kategoriyalar'], summary='Kategoriyani to\'liq yangilash (faqat admin)'),
    patch=extend_schema(tags=['Kategoriyalar'], summary='Kategoriyani qisman yangilash (faqat admin)'),
    delete=extend_schema(tags=['Kategoriyalar'], summary='Kategoriyani o\'chirish (faqat admin)')
)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

@extend_schema_view(
    list=extend_schema(tags=['Mahsulotlar'], summary='Mahsulotlar ro\'yxati (filtrlash, qidiruv, saralash)'),
    retrieve=extend_schema(tags=['Mahsulotlar'], summary='Bitta mahsulot tafsiloti'),
    create=extend_schema(tags=['Mahsulotlar'], summary='Yangi mahsulot yaratish (faqat admin)'),
    update=extend_schema(tags=['Mahsulotlar'], summary='Mahsulotni to\'liq yangilash (faqat admin)'),
    partial_update=extend_schema(tags=['Mahsulotlar'], summary='Mahsulotni qisman yangilash (faqat admin)'),
    destroy=extend_schema(tags=['Mahsulotlar'], summary='Mahsulotni o\'chirish (faqat admin)')
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').prefetch_related('reviews').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    @extend_schema(
        tags=['Mahsulotlar'],
        summary='Mahsulot sharhlari va reytinglarini ko\'rish yoki yangi sharh qoldirish',
        request=ReviewSerializer,
        responses={200: ReviewSerializer(many=True), 201: ReviewSerializer}
    )
    @action(detail=True, methods=['get', 'post'], url_path='reviews', permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def reviews(self, request, pk=None):
        product = self.get_object()

        if request.method == 'GET':
            reviews = product.reviews.select_related('user').all()
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Sharh qoldirish uchun tizimga kirish talab qilinadi.'}, status=status.HTTP_401_UNAUTHORIZED)

        if product.reviews.filter(user=request.user).exists():
            return Response({'detail': 'Siz ushbu mahsulotga allaqachon sharh qoldirgansiz.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
