from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.contrib import messages
from payment.core.subscription.core.subscription_request_core import SubscriptionPaymentRequestDomain
from payment.core.subscription.core.subscription_check_result_core import SubscriptionCheckResult
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='dispatch')
class BuySubscriptionView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
        
        raise PermissionDenied("در حساب کاربری  خود حضور ندارید")
        

    def post(self, request):
        try:
            subscription_payment_request = SubscriptionPaymentRequestDomain(request)
            terminal_redirect_page = subscription_payment_request.execute()
            return redirect(terminal_redirect_page)
        
        except Exception as e:
            messages.error(request, f"{e}", 'danger')
            return redirect("home:index")
    
    
@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='dispatch')
class SubscriptionPayResultView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
        
        raise PermissionDenied("در حساب کاربری  خود حضور ندارید")
    
    def get(self, request):
        try:
            subscription_check_result = SubscriptionCheckResult(request)
            subscription_check_result.execute()
            messages.success(request, "اشتراک با موفقیت خریداری و لحاظ شد", "success")
            return redirect("nurse_users:dashboard")
        
        except Exception as e:
            messages.error(request, f"{e}", 'danger')
            return redirect("home:index")