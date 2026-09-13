from django.views import View 
from django.shortcuts import render, redirect
from nurse_users.models import Skills
from nurse_users.forms import NurseLocationForm
from search_engine.core import search_core
from django.contrib import messages
from extensions.auth_utils_nurse import is_location_within_iran
from extensions.auth_services import map_province_zoom

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

class NearbyNursesView(View):
    def get(self, request):
        coords = map_province_zoom(request)
        context = {
            'skills':Skills.objects.all(),
            'nurse_location_form':NurseLocationForm(),
            "province_lat": coords["lat"],
            "province_lng": coords["lng"],
            "province_zoom": coords["zoom"],
        }
        return render(request, 'nearby_nurses/find_nurse.html', context)
    

@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='post')
class NearbyNurseSearchView(View):
    def post(self, request):
        # get the input 
        location_form = NurseLocationForm(request.POST)
        selected_skill = request.POST.get('province')

        # validate the input 
        if not location_form.is_valid():
            messages.error(request, "اطلاعات نقشه وارد شده صحیح نیست", 'danger')
            return redirect("services:nearby_nurses")
        
        location_data = location_form.cleaned_data['location']
        if not is_location_within_iran(location_data):
            messages.error(request, "موقعیت جغرافیایی خارج از ایران پشتیبانی نمیشود", 'danger')
            return redirect("services:nearby_nurses")

        try:
            selected_skill_instance = Skills.objects.get(id=selected_skill)
        except Exception:
            messages.error(request, "خدمت وارد شده صحیح نیست", 'danger')
            return redirect("services:nearby_nurses")
        
        result = search_core(location_form, selected_skill_instance)

        # add the nurse star to the location dictionary
        for rr in result:
            if rr.nurse_user_additional_info.average_rating:
                rr.full_stars = int(rr.nurse_user_additional_info.average_rating)
                rr.has_half_star = (rr.nurse_user_additional_info.average_rating - rr.full_stars) >= 0.5
            else:
                rr.full_star = None
                rr.has_half_star = False

        context = {
            'nurse_location':result,
            'selected_skill':selected_skill_instance,
        }
        return render(request, 'nearby_nurses/find_nurse_list.html', context)


