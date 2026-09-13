from django.shortcuts import redirect, render, get_object_or_404
from nurse_users.models import NurseUser, NurseSkills, NurseSubSkill
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.views import View

class NurseDetailView(View):
    def get(self, request, slug):
        nurse_user = get_object_or_404(NurseUser, display_user_name=slug)

        if not nurse_user.is_active:
            messages.error(request, "پرستار مورد نظر در انتظار تایید در سامانه است", 'danger')
            return redirect("home:index")
        
        if not nurse_user.has_active_subscription():
            messages.error(request, "پرستار دارای اشتراک فعال نیست", 'danger')
            return redirect("home:index")
        
        # nurse rate 
        nurse_info = nurse_user.nurse_user_additional_info
        if nurse_info.average_rating:
            full_stars = int(nurse_info.average_rating)
            has_half_star = (nurse_info.average_rating - full_stars) >= 0.5
        else:
            full_stars = None
            has_half_star = False

        context = {
            'nurse':nurse_user,
            'nurse_skills':nurse_user.nurse_user_additional_info.nurse_skills.all(),
            
            # nurse rate
            'full_stars':full_stars,
            'has_half_star':has_half_star,
        }

        if nurse_user.is_legal_entity:
            return render(request, 'nurse_users/nurse_detail/nurse_detail_legal.html', context)
        

        return render(request, 'nurse_users/nurse_detail/nurse_detail.html', context)
    

class NurseDetailSkillView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, "برای ارسال درخواست خدمت ابتدا باید وارد حساب کاربری خود شوید", 'danger')
        previous_url = request.META.get('HTTP_REFERER')  # Get the previous page URL
        if previous_url and url_has_allowed_host_and_scheme(previous_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(previous_url)
        else:
            return redirect('home:index')

    
    def get(self, request, nurse_slug, skill_slug):
        # validate the nurse slug 
        nurse = get_object_or_404(NurseUser, display_user_name=nurse_slug)

        # Validate that the nurse has the specified skill
        nurse_skill = get_object_or_404(NurseSkills, nurse=nurse.nurse_user_additional_info, skill__slug=skill_slug)

        nurse_subskills = nurse_skill.nurse_subskill.all()

        if not nurse.is_active:
            messages.error(request, "پرستار مورد نظر در انتظار تایید در سامانه است", 'danger')
            return redirect("home:index")
        
        if not nurse.has_active_subscription():
            messages.error(request, "پرستار دارای اشتراک فعال نیست", 'danger')
            return redirect("home:index")
        
        context = {

            'nurse_core':nurse,
            'nurse_skill':nurse_skill,
            'nurse_subskills':nurse_subskills

        }

        return render(request, 'nurse_users/nurse_detail/nurse_detail_skill.html', context)