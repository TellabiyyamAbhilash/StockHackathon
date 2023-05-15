from django.urls import path
from .views import signup, login, send_otp
from .views import *

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('sendotp/',send_otp, name = 'sendotp'),
    path('stocks/', StockList.as_view(), name='stock-list'),
    path('buy/', BuyApi.as_view(), name='buy'),
    path('sell/', SellApi.as_view(), name='sell'),
]