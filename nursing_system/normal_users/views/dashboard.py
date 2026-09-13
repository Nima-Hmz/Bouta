from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from extensions.auth_utils import is_valid_user_name
from extensions.auth_utils_nurse import is_valid_province
from nurse_users.models import NurseUser
from extensions.auth_services import back_to_previous_page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from services.models import ServiceRequest
from django.views import View

class DashboardView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def get(self, request):
        active_services = ServiceRequest.objects.filter(user=request.user.user_id, status__in=['accepted', 'payment_pending'], closed=False)
        pending_services = ServiceRequest.objects.filter(user=request.user.user_id, status='pending', closed=False)
        context = {
            'user':request.user, 
            'active_services':active_services, 
            'pending_services':pending_services,
        }
        return render(request, 'dashboard/dashboard.html', context)
    

class UpdateBaseView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):
        user_name = request.POST.get('user_name')
        province = request.POST.get('province')
        print(province)

        if not is_valid_user_name(user_name):
            messages.error(request, "نام وارد شده را بررسی کنید", 'danger')
            return redirect("normal_users:user_dashboard")
        
        if not is_valid_province(province):
            messages.error(request, "استان وارد شده را بررسی کنید", 'danger')
            return redirect("normal_users:user_dashboard")
        
        user = request.user

        user.user_name = user_name
        user.province = province

        try:
            user.save()
            messages.success(request, "اطلاعات شما با موفقیت تغییر کرد", 'success')
        except Exception:
            messages.error(request, "خطا در ثبت اطلاعات", 'danger')
            return redirect("normal_users:user_dashboard")

        return redirect('normal_users:user_dashboard')
    

class UserServiceHistory(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def get(self, request):
        service_request_list = ServiceRequest.objects.filter(user=request.user.user_id).exclude(status='pending')
        paginator = Paginator(service_request_list, 9)  # Show 10 subskills per page
        
        page = request.GET.get('page')
        try:
            service_requests = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            service_requests = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver last page of results.
            service_requests = paginator.page(paginator.num_pages)

        # adding nurse first name and last name to the service_requests
        nurse_ids = [sr.nurse for sr in service_requests]

        nurses = NurseUser.objects.filter(custom_user_id__in=nurse_ids)
        nurse_map = {
            nurse.custom_user_id: f"{nurse.first_name} {nurse.last_name}"
            for nurse in nurses
        }

        for sr in service_requests:
            sr.nurse_name = nurse_map.get(sr.nurse, "Unknown Nurse")

        context = {
            'service_requests': service_requests
        }
        return render(request, 'dashboard/service_history.html', context)
    

class ServiceDashboardDetailView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def get(self, request, service_id):
        the_service = get_object_or_404(ServiceRequest, service_request_id=service_id)
        show_nurse_detail = True

        if not the_service.user == request.user.user_id:
            messages.error(request, "خطا در احراز هویت کاربر", 'danger')
            return back_to_previous_page(request)
        
        try:
            the_nurse = NurseUser.objects.get(custom_user_id=the_service.nurse)
        except Exception: 
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return back_to_previous_page(request)
        
        if the_service.status in ['pending', 'reject', 'user_cancelled']:
            show_nurse_detail = False

        # nurse rate 
        nurse_info = the_nurse.nurse_user_additional_info
        if nurse_info.average_rating:
            full_stars = int(nurse_info.average_rating)
            has_half_star = (nurse_info.average_rating - full_stars) >= 0.5
        else:
            full_stars = None
            has_half_star = False
        
        context = {
            "the_service": the_service,
            "service_items": the_service.service_item.all(), 
            "the_user": request.user,
            "the_nurse":the_nurse,
            'show_nurse_detail':show_nurse_detail,
            "payment": getattr(the_service, 'payment', None),   
            "rating": getattr(the_service, 'rating', None),

            # nurse rate
            'full_stars':full_stars,
            'has_half_star':has_half_star,
        }

        return render(request, 'dashboard/service_detail.html', context)