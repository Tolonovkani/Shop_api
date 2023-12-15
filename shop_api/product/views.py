from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, response
from rest_framework.decorators import action

from rating.serializers import RatingSerializer
from .models import Product
from . import serializers
from .permissions import IsAuthor, IsaAuthorOrAdmin


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ProductListSerializer
        return serializers.ProductSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update'):
            return [IsAuthor()]
        elif self.action == 'destroy':
            return [IsaAuthorOrAdmin()]
        return [permissions.IsAuthenticated()]

    # /api/v1/products/<id>/rating/
    @action(['GET', 'POST', 'DELETE'], detail=True)
    def rating(self, request, pk):
        product = self.get_object()
        user = request.user
        is_rating = product.retings.filter(owner=user).exists()

        if request.method == 'GET':
            ratings = product.retings.all()
            serializers = RatingSerializer(instance=ratings, many=True)
            return response.Response(serializers.data, status=200)
        elif request.method == 'POST':
            if is_rating:
                return response.Response('You already rated this product',
                                         status=400)
            data = request.data
            serializer = RatingSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=user, product=product)
            return response.Response(serializer.data, status=201)
        else:
            if not is_rating:
                return response.Response('You didn\'t rated this product',
                                         status=400)
            rating = product.retings.get(owner=user)
            rating.delete()
            return response.Response('Deleted!', status=204)