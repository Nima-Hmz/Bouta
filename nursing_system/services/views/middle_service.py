from django.shortcuts import render, redirect, get_object_or_404
from services.service_limitations import check_nurse_cancel_service, check_user_middle_cancel_service, \
    check_nurse_end_service, check_user_end_service
from services.models import ServiceRequest
from django.views import View
from nurse_users.models import NurseUser
from extensions.auth_services import back_to_previous_page
from django.contrib import messages

# what are the service middle actions ? : 
# 1) nurse cancel service 
# 2) nurse end service 
# 3) user cancel service
# 4) user end service


class NurseCancelServiceView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def post(self, request, service_id):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return back_to_previous_page(request)
        
        the_service = get_object_or_404(ServiceRequest, service_request_id=service_id)

        if not nurse_user.is_active:
            messages.error(request, "پرستار مورد نظر در انتظار تایید در سامانه است", 'danger')
            return back_to_previous_page(request)

        if not nurse_user.has_active_subscription():
            messages.error(request, "پرستار دارای اشتراک فعال نیست", 'danger')
            return back_to_previous_page(request)
        
        if not the_service.nurse == nurse_user.custom_user_id:
            messages.error(request, "خطا در احراز هویت پرستار", 'danger')
            return back_to_previous_page(request)
        
        # check if limits are ok: 
        is_valid_limit, limit_message = check_nurse_cancel_service(service=the_service)

        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        cancel_result = the_service.nurse_cancel_service()
        if not cancel_result:
            messages.error(request, "خطا در لغو کردن خدمت", 'danger')
            return back_to_previous_page(request)
        
        messages.success(request, "درخواست خدمت لغو شد.", 'success')
        return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
    

class UserMiddleCancelServiceView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def post(self, request, service_id):
        the_service = get_object_or_404(ServiceRequest, service_request_id=service_id)
        if not the_service.user == request.user.user_id:
            messages.error(request, "خطا در احراز هویت کاربر", 'danger')
            return back_to_previous_page(request)
        
        # check if the limits are ok:
        is_valid_limit, limit_message = check_user_middle_cancel_service(service=the_service)

        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        cancel_service = the_service.user_middle_cancel_service()
        if not cancel_service:
            messages.error(request, "خطا در لغو خدمت", 'danger')
            return back_to_previous_page(request)
        
        messages.success(request, "درخواست خدمت لغو شد.", 'success')
        return redirect('normal_users:service_detail', service_id=the_service.service_request_id)
    

class NurseEndServiceView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def post(self, request, service_id):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return back_to_previous_page(request)
        
        the_service = get_object_or_404(ServiceRequest, service_request_id=service_id)

        if not nurse_user.is_active:
            messages.error(request, "پرستار مورد نظر در انتظار تایید در سامانه است", 'danger')
            return back_to_previous_page(request)

        if not nurse_user.has_active_subscription():
            messages.error(request, "پرستار دارای اشتراک فعال نیست", 'danger')
            return back_to_previous_page(request)
        
        if not the_service.nurse == nurse_user.custom_user_id:
            messages.error(request, "خطا در احراز هویت پرستار", 'danger')
            return back_to_previous_page(request)
        
        # check if the limits are ok:
        is_valid_limit, limit_message = check_nurse_end_service(service=the_service)

        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        end_result = the_service.nurse_end_service()
        if not end_result:
            messages.error(request, "خطا در پایان دادن خدمت", 'danger')
            return back_to_previous_page(request)
        
        messages.success(request, "پایان کار پرستار با موفقیت اعلام شد", 'success')
        return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
    

class UserEndServiceView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def post(self, request, service_id):
        the_service = get_object_or_404(ServiceRequest, service_request_id=service_id)

        if not the_service.user == request.user.user_id:
            messages.error(request, "خطا در احراز هویت کاربر", 'danger')
            return back_to_previous_page(request)
        
        # check if the limits are ok:
        is_valid_limit, limit_message = check_user_end_service(service=the_service)

        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        end_result = the_service.user_end_service()
        if not end_result:
            messages.error(request, "خطا در ارسال درخواست پایان خدمت", 'danger')
            return back_to_previous_page(request)
        
        messages.success(request, "درخواست پایان خدمت ارسال شد", 'success')
        return redirect('normal_users:service_detail', service_id=the_service.service_request_id)