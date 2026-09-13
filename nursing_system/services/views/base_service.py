from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import get_object_or_404
from normal_users.models import CustomUser
from nurse_users.models import NurseUser, NurseSkills, NurseSubSkill
from services.models import ServiceRequest, ServiceItem, Payment, Rating
from extensions.auth_services import is_validate_quantity, back_to_previous_page, validate_long_message, \
    send_sms
from django.contrib import messages
from services.service_limitations import check_user_request_service_limits, \
    check_nurse_accept_service, check_nurse_reject_service, check_user_cancel_service
from django.db import transaction
from django.views import View
from django.http import HttpResponse

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

# what are the service base actions ? : 
# 1) service create(the request by the user)
# 2) service accept nurse 
# 3) service reject nurse 
# 4) service cancel user  

@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='post')
class ServiceCreateView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                messages.error(request, "با حساب پرستار نمیتوانید درخواست خدمت ارسال کنید", 'danger')
                return redirect('home:index')
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, "برای ارسال درخواست خدمت ابتدا باید وارد حساب کاربری خود شوید", 'danger')
        previous_url = request.META.get('HTTP_REFERER')  # Get the previous page URL
        if previous_url and url_has_allowed_host_and_scheme(previous_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(previous_url)
        else:
            return redirect('home:index')
    
    def post(self, request, nurse_slug, skill_slug):
        # validate the nurse slug 
        nurse = get_object_or_404(NurseUser, display_user_name=nurse_slug)

        # Validate that the nurse has the specified skill
        nurse_skill = get_object_or_404(NurseSkills, nurse=nurse.nurse_user_additional_info, skill__slug=skill_slug)

        # validate the nurse activate account and subscription
        if not nurse.is_active:
            messages.error(request, "پرستار مورد نظر در انتظار تایید در سامانه است", 'danger')
            return redirect("home:index")
        
        if not nurse.has_active_subscription():
            messages.error(request, "پرستار دارای اشتراک فعال نیست", 'danger')
            return redirect("home:index")
        
        # validate long message
        description = request.POST.get('long_message')
        is_valid_message, message_description = validate_long_message(description)
        if not is_valid_message:
            messages.error(request, f"{message_description}", 'danger')
            return back_to_previous_page(request)

        # validate the subskills
        subskill_ids = request.POST.getlist("nurse_subskill_id")
        valid_subskills = NurseSubSkill.objects.filter(nurse=nurse.nurse_user_additional_info, id__in=subskill_ids)
        subskill_and_quantity= {}
        
        for nurse_subskill in valid_subskills:
            # Retrieve the new price input; form field name is like custom_price_123 where 123 is nurse_subskill.id
            quantity_input = request.POST.get(f"subskill_{nurse_subskill.id}", "").strip()

            is_valid_quantity, message = is_validate_quantity(quantity_input)
            if not is_valid_quantity:
                messages.error(request, f"ورودی نامعتبر {message}", 'danger')
                return back_to_previous_page(request)

            quantity_input = message # it will be a number if returns true
            subskill_and_quantity[nurse_subskill] = quantity_input # put it in a dictionary

        # check if the quantity is set 
        if not any(value > 0 for value in subskill_and_quantity.values()):
            messages.error(request, "شما هیچ خدمتی را مشخص نکرده‌اید", 'danger')
            return back_to_previous_page(request)
        

        # check if the limits are ok:
        is_valid_limit, limit_message = check_user_request_service_limits(user_instance=request.user, \
                                                                          nurse_instance=nurse)
        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)

                
        # Use an atomic transaction for the database writes
        try:
            with transaction.atomic():
                service_instance = ServiceRequest.objects.create(
                    skill_slug=skill_slug,
                    skill_title=nurse_skill.skill.title,
                    user=request.user.user_id,
                    nurse=nurse.custom_user_id,
                    service_detail_user=description
                )
                for nurse_subskill, quantity in subskill_and_quantity.items():
                    if quantity > 0:
                        ServiceItem.objects.create(
                            service=service_instance,
                            subskill=nurse_subskill.nurse_subskill_uuid,
                            subskill_title=nurse_subskill.subskill.title,
                            price=nurse_subskill.custom_price,
                            quantity=quantity
                        )
                Payment.objects.create(service_request=service_instance, amount=service_instance.get_total_price())
                Rating.objects.create(service_request=service_instance)
        except Exception as e:
            messages.error(request, "خطایی در ثبت درخواست خدمت رخ داده است", 'danger')
            return back_to_previous_page(request)
        
        try:
            send_sms(phone_number=nurse.phone_number, message="پرستار گرامی درخواست خدمت جدید به حساب شما ارسال شده است")
        except Exception:
            messages.error(request, "خطا در ارسال پیامک دریافت خدمت به پرستار", 'danger')
            
        messages.success(request, "درخواست خدمت شما به پرستار ارسال شد", 'success')
        return redirect("nurse_users:nurse_detail", slug=nurse_slug)


class NurseAcceptServiceView(View):
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

        try:
            the_user = CustomUser.objects.get(user_id=the_service.user)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات کاربر", 'danger')
            return back_to_previous_page(request)

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
        is_valid_limit, limit_message = check_nurse_accept_service(service=the_service, \
                                                                    nurse=nurse_user)
        
        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        accept_result = the_service.accept_and_cancel_others()
        if not accept_result:
            messages.error(request, "خطا در پذیرفتن خدمت", 'danger')
            return back_to_previous_page(request)
        
        try:
            send_sms(the_user.phone_number, 'درخواست خدمت شما توسط پرستار پذیرفته شد')
        except Exception:
            messages.error(request, "خطا در ارسال پیام اطلاع رسانی به کاربر", 'danger')

        messages.success(request, "درخواست با موفقیت پذیرفته شد.", 'success')
        return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
                        
            
class NurseRejectServiceView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def post(serlf, request, service_id):
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
        is_valid_limit, limit_message = check_nurse_reject_service(service=the_service)

        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        reject_result = the_service.reject_service()
        if not reject_result:
            messages.error(request, "خطا در رد کردن خدمت", 'danger')
            return back_to_previous_page(request)
        
        messages.success(request, "درخواست خدمت رد شد.", 'success')
        return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
    

class UserCancelServiceView(View):
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
        is_valid_limit, limit_message = check_user_cancel_service(service=the_service)

        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        cancel_service = the_service.user_cancel_service()
        if not cancel_service:
            messages.error(request, "خطا در لغو خدمت", 'danger')
            return back_to_previous_page(request)
        
        messages.success(request, "درخواست خدمت لفو شد.", 'success')
        return redirect('normal_users:service_detail', service_id=the_service.service_request_id)