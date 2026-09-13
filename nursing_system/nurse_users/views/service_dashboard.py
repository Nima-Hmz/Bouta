from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from extensions.auth_services import back_to_previous_page
from normal_users.models import CustomUser
from services.models import ServiceRequest, NurseWallet
from nurse_users.models import NurseUser
from normal_users.models import CustomUser
from django.contrib import messages

class ServiceDashboardView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def get(self, request):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_walet = NurseWallet.objects.get(nurse_id=nurse_user.custom_user_id)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return redirect('home:index')

        active_services = ServiceRequest.objects.filter(nurse=nurse_user.custom_user_id, status__in=['accepted', 'payment_pending'], closed=False)
        pending_services = ServiceRequest.objects.filter(nurse=nurse_user.custom_user_id, status='pending', closed=False)

        # nurse rate 
        nurse_info = nurse_user.nurse_user_additional_info
        if nurse_info.average_rating:
            full_stars = int(nurse_info.average_rating)
            has_half_star = (nurse_info.average_rating - full_stars) >= 0.5
        else:
            full_stars = None
            has_half_star = False

        context = {
            'active_services':active_services, 
            'pending_services':pending_services,
            'wallet':nurse_walet,
            'nurse':nurse_user,

            # nurse rate
            'full_stars':full_stars,
            'has_half_star':has_half_star,
        }
        return render(request, 'nurse_users/dashboard/service_dashboard.html', context)
    

class NurseServiceHistory(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def get(self, request):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return redirect('home:index')
        
        service_request_list = ServiceRequest.objects.filter(nurse=nurse_user.custom_user_id).exclude(status='pending')
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
        user_ids = [sr.user for sr in service_requests]

        users = CustomUser.objects.filter(user_id__in=user_ids)
        user_map = {
            user.user_id: user.user_name
            for user in users
        }

        for sr in service_requests:
            sr.user_name = user_map.get(sr.user, "Unknown Nurse")

        context = {
            'service_requests': service_requests
        }

        return render(request, 'nurse_users/dashboard/service_history.html', context)
    

class ServiceDashboardDetailView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def get(self, request, service_id):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return back_to_previous_page(request)
        
        the_service = get_object_or_404(ServiceRequest, service_request_id=service_id)

        if not the_service.nurse == nurse_user.custom_user_id:
            messages.error(request, "خطا در احراز هویت پرستار", 'danger')
            return back_to_previous_page(request)
        
        try:
            the_user = CustomUser.objects.get(user_id=the_service.user)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات کاربر", 'danger')
            return back_to_previous_page(request)
        
        # user stars
        if the_user.average_rating:
            full_stars = int(the_user.average_rating)
            has_half_star = (the_user.average_rating - full_stars) >= 0.5
        else:
            full_stars = None
            has_half_star = False

        
        context = {
            "the_service": the_service,
            "service_items": the_service.service_item.all(), 
            "the_user": the_user,
            "payment": getattr(the_service, 'payment', None),   
            "rating": getattr(the_service, 'rating', None),  

            # user stars 
            'full_stars':full_stars,
            'has_half_star':has_half_star,  
        }
        
        return render(request, 'nurse_users/dashboard/service_detail.html', context)

