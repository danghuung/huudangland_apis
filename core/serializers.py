from rest_framework.serializers import ModelSerializer
from .models import CountyCategory, Product, ParameterLR, Customer, Comment, Predict


class CountyCategorySerializer(ModelSerializer):
    class Meta:
        model = CountyCategory
        fields = ['id', 'county_keyword', 'county_name']


class ProductSerializer(ModelSerializer):
    county = CountyCategory()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'area', 'floors', 'location', 'to_center',
                'predict_price', 'price', 'address', 'county', 'create_date', 'update_date']


class ParameterSerializer(ModelSerializer):
    class Meta:
        model = ParameterLR
        fields = '__all__'


class CustomerSerializer(ModelSerializer):
    def create(self, validated_data):
        customer = Customer(**validated_data)
        customer.set_password(customer.password)
        customer.save()

        return customer

    class Meta:
        model = Customer
        fields = ['phone_number', 'name_customer', 'date_of_birth', 'gender', 'time']

    extra_kwargs = {
        'password': 'true'
    }


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'create_date', 'update_date']

    
class PredictSerializer(ModelSerializer):
    class Meta:
        model = Predict
        fields = ['id', 'area', 'floors', 'location', 'to_center', 'predict_price', 'create_date']