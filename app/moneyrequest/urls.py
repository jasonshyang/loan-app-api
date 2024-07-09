from django.urls import path, include

from rest_framework.routers import DefaultRouter

from moneyrequest import views


router = DefaultRouter()
router.register('moneyrequests', views.MoneyRequestViewSet)

app_name = 'moneyrequest'

urlpatterns = [
    path('', include(router.urls)),
]