from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from services.models import ServiceRequest, UserReport, NurseReport
from normal_users.models import CustomUser
from django.db.models import Avg
from django.db import transaction
from nurse_users.models import NurseUser
from services.service_limitations import check_user_rate, check_nurse_rate
from extensions.auth_services import back_to_previous_page, validate_long_message, \
    is_valid_description_report
from django.views import View 


# what are the service middle actions ? : 
# 1) user rate service
# 2) nurse rate service
# 3) user report service 
# 4) nurse report service

class UserRateServiceView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def post(self, request, service_id):
        the_service = get_object_or_404(ServiceRequest, service_request_id=service_id)

        try:
            nurse_user = NurseUser.objects.get(custom_user_id=the_service.nurse)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return back_to_previous_page(request)
        
        if not the_service.user == request.user.user_id:
            messages.error(request, "خطا در احراز هویت کاربر", 'danger')
            return back_to_previous_page(request)
        
        if the_service.rating.user_rating is not None:
            messages.error(request, "شما قبلا امتیاز داده اید", 'danger')
            return redirect('normal_users:service_detail', service_id=the_service.service_request_id)
        
        # check if the limits are ok:
        is_valid_limit, limit_message = check_user_rate(service=the_service)

        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        stars = request.POST.get('stars')
        user_comment = request.POST.get('user_comment')

        try:
            stars = int(stars)
            if stars < 1 or stars > 5:
                messages.error(request, "امتیاز خود را بین ۱ تا ۵ وارد کنید", 'danger')
                return redirect('normal_users:service_detail', service_id=the_service.service_request_id)
        except Exception:
            messages.error(request, "امتیاز خود را بین ۱ تا ۵ وارد کنید", 'danger')
            return redirect('normal_users:service_detail', service_id=the_service.service_request_id)
        
        is_valid_comment, comment_message = validate_long_message(user_comment)
        if not is_valid_comment:
            messages.error(request, f"{comment_message}", 'danger')
            return back_to_previous_page(request)   

        try:
            with transaction.atomic():
                the_service.rating.user_rating = stars     
                the_service.rating.user_review = user_comment 
                the_service.rating.save()

                nurse_info = nurse_user.nurse_user_additional_info

                old_count = nurse_info.rating_count or 0
                old_avg = nurse_info.average_rating or 0
                new_count = old_count + 1

                new_avg = stars if old_count == 0 else ((old_avg * old_count) + stars) / new_count
                nurse_info.rating_count = new_count
                nurse_info.average_rating = new_avg

                nurse_info.save(update_fields=['average_rating', 'rating_count'])

                messages.success(request, "نظر شما با موفقیت ثبت شد", 'success')
        except Exception:
            messages.error(request, "خطا در ثبت نظر", 'danger')
            return redirect('normal_users:service_detail', service_id=the_service.service_request_id)
        
        return redirect('normal_users:service_detail', service_id=the_service.service_request_id)


class NurseRateServiceView(View):
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
        
        if the_service.rating.nurse_rating is not None:
            messages.error(request, "شما قبلا امتیاز داده اید", 'danger')
            return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
        
        # check if the limits are ok:
        is_valid_limit, limit_message = check_nurse_rate(service=the_service)

        if not is_valid_limit:
            messages.error(request, f"{limit_message}", 'danger')
            return back_to_previous_page(request)
        
        stars = request.POST.get('stars')
        nurse_comment = request.POST.get('nurse_comment')

        try:
            stars = int(stars)
            if stars < 1 or stars > 5:
                messages.error(request, "امتیاز خود را بین ۱ تا ۵ وارد کنید", 'danger')
                return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
        except Exception:
            messages.error(request, "امتیاز خود را بین ۱ تا ۵ وارد کنید", 'danger')
            return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
        
        is_valid_comment, comment_message = validate_long_message(nurse_comment)
        if not is_valid_comment:
            messages.error(request, f"{comment_message}", 'danger')
            return back_to_previous_page(request)

        try:
            with transaction.atomic():
                # save the comment 
                the_service.rating.nurse_rating = stars     
                the_service.rating.nurse_review = nurse_comment 
                the_service.rating.save()


                old_count = the_user.rating_count or 0
                old_avg = the_user.average_rating or 0
                new_count = old_count + 1

                new_avg = stars if old_count == 0 else ((old_avg * old_count) + stars) / new_count
                the_user.rating_count = new_count
                the_user.average_rating = new_avg

                the_user.save(update_fields=['average_rating', 'rating_count'])

                messages.success(request, "نظر شما با موفقیت ثبت شد", 'success')
        except Exception:
            messages.error(request, "خطا در ثبت نظر", 'danger')
            return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
        
        return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)


class UserReportView(View):
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
        
        if UserReport.objects.filter(service_id=service_id).exists():
            messages.error(request, "شما قبلا گزارش خود را ارسال کرده اید", 'danger')
            return back_to_previous_page(request)
        
        description = request.POST.get('report_description')

        is_valid_description , message = is_valid_description_report(description)
        if not is_valid_description:
            messages.error(request, f"{message}", 'danger')
            return back_to_previous_page(request)
        
        try:
            UserReport.objects.create(service_id=service_id, description=description)
            messages.success(request, "گزارش شما با موفقیت ثبت شد همکاران ما در سریع ترین زمان ممکن آن را بررسی میکنند", 'success')
        except Exception:
            messages.error(request, "خطا در ثبت گزارش", 'danger')
            return back_to_previous_page(request)

        return redirect('normal_users:service_detail', service_id=the_service.service_request_id)
        

class NurseReportView(View):
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

        if not the_service.nurse == nurse_user.custom_user_id:
            messages.error(request, "خطا در احراز هویت پرستار", 'danger')
            return back_to_previous_page(request)
        
        if NurseReport.objects.filter(service_id=service_id).exists():
            messages.error(request, "شما قبلا گزارش خود را ارسال کرده اید", 'danger')
            return back_to_previous_page(request)
        
        description = request.POST.get('report_description')

        is_valid_description , message = is_valid_description_report(description)
        if not is_valid_description:
            messages.error(request, f"{message}", 'danger')
            return back_to_previous_page(request)

        try:
            NurseReport.objects.create(service_id=service_id, description=description)
            messages.success(request, "گزارش شما با موفقیت ثبت شد همکاران ما در سریع ترین زمان ممکن آن را بررسی میکنند", 'success')
        except Exception:
            messages.error(request, "خطا در ثبت گزارش", 'danger')
            return back_to_previous_page(request)
        
        return redirect('nurse_users:service_detail', service_id=the_service.service_request_id)
        