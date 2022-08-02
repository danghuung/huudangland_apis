from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("county", views.CounterCategoryViewSet, 'county')
router.register("parameters", views.ParameterViewSet, 'parameter')
router.register("products", views.ProductViewSet, 'product')
router.register("customers", views.CustomerViewSet, 'customer')
router.register("comments", views.CommentViewSet, 'comment')
router.register("predicts", views.PredictViewSet, 'predict')

urlpatterns = [
    path('', include(router.urls)),
    path('oauth2-info/', views.UserAuthInfo.as_view())
]