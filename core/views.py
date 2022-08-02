from rest_framework import viewsets, generics, status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import (
    CountyCategorySerializer, 
    ProductSerializer, 
    ParameterSerializer,
    CustomerSerializer,
    CommentSerializer,
    PredictSerializer
)
from .models import CountyCategory, Product, ParameterLR, Customer, Comment, Predict
from .predict import predict
from django.conf import settings
from django.db.models import Q
from django.core.mail import send_mail
# Create your views here.


class CounterCategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    serializer_class = CountyCategorySerializer
    queryset = CountyCategory.objects.filter(is_active=True)


class ParameterViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveUpdateAPIView):
    serializer_class = ParameterSerializer
    queryset = ParameterLR.objects.filter(is_active=True)
    permission_classes = [permissions.IsAdminUser]


class CustomerViewSet(viewsets.ViewSet, generics.ListCreateAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action == "get_current_user":
            return [permissions.IsAuthenticated()]
        
        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path="current-user")
    def get_current_user(self, request):
        return Response(self.serializer_class(request.user).data, status=status.HTTP_200_OK)


class ProductViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['destroy', 'create_product', 'partial_update', 'add_comment']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]
    
    def get_queryset(self):
        product = Product.objects.filter(is_active=True)

        search = self.request.query_params.get('search')
        if search is not None:
            product = Product.objects.filter(Q(product_name__icontains=search) | Q(address__icontains=search))

        return product

    @action(methods=['post'], detail=False, url_path="create-product")
    def create_product(self, request):
        product_name = request.data.get('product_name')
        area = request.data.get('area')
        floors = request.data.get('floors')
        location = request.data.get('location')
        to_center = request.data.get('to_center')
        price = request.data.get('price')
        address = request.data.get('address')
        county_id = request.data.get('county')

        variable_list = [1, area, floors, location, to_center]
        predict_class = predict(variable_list)
        predict_price = predict_class.predict_price()

        predict_price = str(predict_price)
        predict_price = predict_price.split('.')[0]
        predict_price = predict_price + '000000'

        if product_name:
            p = Product.objects.create(product_name=product_name, 
                                        area=area, 
                                        floors=floors,
                                        location=location, 
                                        to_center=to_center,
                                        price=price, address=address,
                                        predict_price = float(predict_price),
                                        county=CountyCategory.objects.get(pk=county_id))

            return Response(ProductSerializer(p).data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def partial_update(self, request, *args, **kwargs):
        m = self.get_object()
        predict_price = m.predict_price
        super().partial_update(request, *args, **kwargs)
        p = self.get_object()

        variable_list = [1, p.area, p.floors, p.location, p.to_center]
        predict_class = predict(variable_list)
        predict_price_new = predict_class.predict_price()

        predict_price_new = str(predict_price_new)
        predict_price_new = predict_price_new.split('.')[0]
        predict_price_new = predict_price_new + '000000'

        if predict_price != int(predict_price_new):
            Product.objects.filter(pk=p.id).update(predict_price=int(predict_price_new))

            return Response(ProductSerializer(p).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path="add-comment")
    def add_comment(self, request, pk):
        content = request.data.get('content')
        if content:
            c = Comment.objects.create(content=content,
                                        creator = request.user,
                                        product = self.get_object())
            
            return Response(CommentSerializer(c).data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView, generics.ListAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().creator:
            return super().destroy(request, *args, **kwargs)

        return Response(status=status.HTTP_403_FORBIDDEN)

    def partial_update(self, request, *args, **kwargs):
        if request.user == self.get_object().creator:
            return super().partial_update(request, *args, **kwargs)

        return Response(status=status.HTTP_403_FORBIDDEN)


class PredictViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Predict.objects.all()
    serializer_class = PredictSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['post'], detail=False, url_path="predict-price")
    def predict_price(self, request):
        area = request.data.get('area')
        floors = request.data.get('floors')
        location = request.data.get('location')
        to_center = request.data.get('to_center')
        email = request.data.get('email')

        variable_list = [1, area, floors, location, to_center]
        predict_class = predict(variable_list)
        predict_price = predict_class.predict_price()

        predict_price = str(predict_price)
        predict_price = predict_price.split('.')[0]
        predict_price = predict_price + '000000'

        subject = "Dinh Gia Bat Dong San"
        msg = "Ban vua su dung chuc nang dinh gia, Gia tri dinh gia la: "+predict_price

        if predict_price:
            send_mail(subject, msg, 'dinhgianhadat.cantho@gmail.com', [email], fail_silently=False)

        try:
            pred = Predict.objects.create(area=area, 
                                            floors=floors,
                                            location=location, 
                                            to_center=to_center,
                                            predict_price = float(predict_price),
                                            predict_customer = request.user,
                                            email = email)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(PredictSerializer(pred).data, status=status.HTTP_201_CREATED)


class UserAuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)