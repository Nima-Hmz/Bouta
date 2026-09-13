from django.urls import path
from .api.nurse_subscription_api import BuySubscriptionView, SubscriptionPayResultView
from .api.user_service_payment import UserServicePaymentView, UserServicePayResultView

app_name = 'payment'

urlpatterns = [
    path('buy-nurse-subscription/', BuySubscriptionView.as_view(), name='buy-nurse-subscription'),
    path('subscription-result/', SubscriptionPayResultView.as_view(), name='get_back'),

    path('user-service-payment/<slug:service_id>/', UserServicePaymentView.as_view(), name="user_service_payment"),
    path('user-service-payment-result/', UserServicePayResultView.as_view(), name="user_service_payment_result"),
    
]
