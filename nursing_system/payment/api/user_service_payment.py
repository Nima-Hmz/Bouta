from typing import Any
from payment.core.service_payment.core.service_payment_request_core import ServicePaymentRequest
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.views import View
from django.core.exceptions import PermissionDenied
from payment.core.service_payment.core.service_check_result import ServicePaymentCheckResult

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='dispatch')
class UserServicePaymentView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        raise PermissionDenied("در حساب کاربری  خود حضور ندارید")

    def post(self, request, service_id):
        try:
            service_payment_request = ServicePaymentRequest(request, service_id)
            terminal_redirect_page = service_payment_request.execute()
            return redirect(terminal_redirect_page)
        
        except Exception as e:
            messages.error(request, f"{e}", 'danger')
            return redirect("home:index")
        

@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='dispatch')
class UserServicePayResultView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied("در حساب کاربری  خود حضور ندارید")
    
    def get(self, request):
        try:
            service_payment_check_result = ServicePaymentCheckResult(request)
            the_service_request = service_payment_check_result.execute()
            messages.success(request, "خدمت با موفقیت پرداخت شد", "success")
            return redirect("normal_users:service_detail", service_id=the_service_request.service_request_id)
        except Exception as e:
            messages.error(request, f"{e}", 'danger')
            return redirect("home:index")
        