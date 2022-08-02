from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class CustomerManager(BaseUserManager):
    def create_user(self, phone_number, name_customer, date_of_birth, gender, password=None):
        if not phone_number:
            raise ValueError('phone number is required')
        if not name_customer:
            raise ValueError('name is required')
        if not date_of_birth:
            raise ValueError('date of birth is required')
        if not gender:
            raise ValueError('is required')
 
        user=self.model(
            phone_number=phone_number,
            name_customer=name_customer,
            date_of_birth=date_of_birth,
            gender=gender
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name_customer, date_of_birth, gender, password=None):
        user=self.create_user(
            phone_number=phone_number,
            name_customer=name_customer,
            date_of_birth=date_of_birth,
            gender=gender,
            password=password
        )
        user.is_admin=True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user

class Customer(AbstractBaseUser):
    phone_number = models.CharField(max_length=10, default='', primary_key=True)
    name_customer = models.CharField(max_length=100, default='')
    date_of_birth = models.CharField(max_length=10, default='')
    gender = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now=True, null=True)
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name_customer', 'date_of_birth', 'gender']

    objects = CustomerManager()

    def __str__(self):
        return self.phone_number

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class MyModelBase(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class CountyCategory(MyModelBase):
    county_keyword = models.CharField(default='', max_length=5)
    county_name = models.CharField(default='', max_length=255)

    def __str__(self):
        return self.county_name


class ProductModelBase(models.Model):
    area = models.FloatField(default=0.0, null=False)
    floors = models.IntegerField(default=0, null=False)
    location = models.IntegerField(default=0, null=False)
    to_center = models.FloatField(default=0.0, null=False)
    predict_price = models.FloatField(default=0.0)

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Product(ProductModelBase):
    class Meta:
        ordering = ["-id"]

    product_name = models.CharField(max_length=255, default='', null=False)
    price = models.FloatField(default=0.0)
    address = models.CharField(max_length=255, default='')
    county = models.ForeignKey(CountyCategory, on_delete=models.CASCADE)
    image = models.TextField(default='')

    def __str__(self):
        return self.product_name


class ParameterLR(MyModelBase):
    parameter = models.CharField(max_length=255, default='')
    is_using = models.IntegerField(default=0)


class Comment(MyModelBase):
    class Meta:
        ordering = ["-id"]

    content = models.TextField(null=False)
    creator = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class Predict(ProductModelBase):
    class Meta:
        ordering = ["-id"]

    predict_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    email = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.email