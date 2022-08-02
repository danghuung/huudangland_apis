from django.contrib import admin
from .models import CountyCategory, Product, ParameterLR

# Register your models here.
admin.site.register(CountyCategory)
admin.site.register(Product)
admin.site.register(ParameterLR)
