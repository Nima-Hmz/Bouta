from django.views import View 
from django.shortcuts import render, redirect
from extensions.auth_utils_nurse import is_valid_name, is_valid_image, is_valid_sex, \
    is_valid_address, jalali_convertor, is_valid_work_experience, is_valid_price, is_valid_province, \
    is_location_within_iran, is_valid_description, check_national_id_number
from extensions.auth_services import is_valid_display_name, map_province_zoom
from extensions.auth_utils import is_valid_phone_number
from django.contrib import messages
from django.db import transaction
from nurse_users.models import NurseUser, EducationLevel, Skills, AdditionalKnowledg, \
    ModernNursing, WorkingHours, NurseSkills, WorkExperience, NurseSubSkill
from nurse_users.forms import WorkingHoursForm, NurseLocationForm
from django.utils import timezone
from datetime import timedelta
import os
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.http import HttpResponseNotAllowed


class DashboardView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
        

    def get(self, request):
        user_id = request.user.user_id
        all_skills = Skills.objects.all()
        all_additional_knowledg = AdditionalKnowledg.objects.all()
        all_modern_nursing = ModernNursing.objects.all()
        coords = map_province_zoom(request)

        try : 
            nurse_user = NurseUser.objects.get(custom_user_id=user_id)
            nurse_user_additional_info = nurse_user.nurse_user_additional_info
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return redirect('home:index')

        # get the nurse location 
        existing_location = None
        if nurse_user_additional_info.nurse_location:
            existing_location =nurse_user_additional_info.nurse_location.location

        context = {

            'nurse_core':nurse_user,
            'education_levels': EducationLevel.objects.all(),
            'all_skills':all_skills,
            'all_additional_knowledg': all_additional_knowledg,
            'all_modern_nursing': all_modern_nursing,

            # selected additional info
            'selected_skill_ids': set(nurse_user_additional_info.nurse_skills.values_list('skill__id', flat=True)),
            'selected_knowledge':nurse_user_additional_info.additional_knowledg.all(),
            'selected_nursing':nurse_user_additional_info.modern_nursing,

            # selected subskill info
            'selected_subskill_model':nurse_user_additional_info.nurse_subskill.all(),

            # woking hours
            'working_hours_form':WorkingHoursForm(),
            'nurse_location_form':NurseLocationForm(),

            # the nurse location
            "existing_location": existing_location,

            # map default zoom on nurse province (if there were no location saved)
            "province_lat": coords["lat"],
            "province_lng": coords["lng"],
            "province_zoom": coords["zoom"],

        }
        return render(request, 'nurse_users/dashboard/dashboard.html', context)
    

class UpdateBaseView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):        
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            registeration_request = nurse_user.register_request
        except Exception:
            messages.error(request, "حساب پرستار یافت نشد", 'danger')
            return redirect('home:index')
        
        now = timezone.now()
        if registeration_request.updated_at > now - timedelta(hours=1):
            messages.error(request, "شما هر ۱ ساعت یک بار توانایی ایجاد تغییر اطلاعات حساب خود را دارید", "danger")
            return redirect('nurse_users:dashboard')

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_name = request.POST.get('display_user_name')
        birthday = request.POST.get('birthday')
        province = request.POST.get('province')
        city = request.POST.get('city')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        ministry_proof_picture = request.FILES.get('ministry_proof_picture')
        profile_picture = request.FILES.get('profile_picture')
        sex = request.POST.get('sex')
        education_level_id = request.POST.get('education_level') 
        national_id_number = request.POST.get('national_id_number')
        identity_card_picture = request.FILES.get('identity_card_picture')
        

        if not is_valid_name(first_name):
            messages.error(request, "نام وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")

        if not is_valid_name(last_name):
            messages.error(request, "نام خانوادگی وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")

        try: 
            gregorian_date = jalali_convertor(birthday) 
        except Exception:
            messages.error(request, "تاریخ تولد وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")   
        
        if not is_valid_province(province):
            messages.error(request, "استان وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")
        
        if not is_valid_name(city):
            messages.error(request, "شهر وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")
        
        if not is_valid_phone_number(phone_number):
            messages.error(request, "شماره موبایل وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")
        
        if not is_valid_address(address):
            messages.error(request, "آدرس وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")
        
        if not is_valid_sex(sex):
            messages.error(request, "جنیست وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")
        
        try:
            ed_level_instance = EducationLevel.objects.get(id=education_level_id)
        except Exception:
            messages.error(request, "مدرک تحصیلی وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")
        
        if user_name != nurse_user.display_user_name:
            is_valid_user_name, message = is_valid_display_name(user_name)
            if not is_valid_user_name:
                messages.error(request, f"{message}", 'danger')
                return redirect("nurse_users:dashboard")
        
        if not check_national_id_number(national_id_number):
            messages.error(request, "کد ملی وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")


        # update the info
        if profile_picture:
            # check if the profile picture is valid valid
            if not is_valid_image(profile_picture):
                messages.error(request, "عکس پرستار وارد شده را بررسی کنید", 'danger')
                return redirect("nurse_users:register")
            # delete the old one & set the new one 
            if nurse_user.profile_picture:
                nurse_user.profile_picture.delete(save=False)

            nurse_user.profile_picture = profile_picture

        if ministry_proof_picture:
            # check if the ministry_proof_picture is valid
            if not is_valid_image(ministry_proof_picture):
                messages.error(request, "گواهی تایید وارد شده را بررسی کنید", 'danger')
                return redirect("nurse_users:register")
            # delete the old one & set the new one 
            if nurse_user.ministry_proof_picture:
                nurse_user.ministry_proof_picture.delete(save=False)

            nurse_user.ministry_proof_picture = ministry_proof_picture

        if identity_card_picture:
            if not is_valid_image(identity_card_picture):
                messages.error(request, "کارت شناسایی وارد شده را بررسی کنید", 'danger')
                return redirect("nurse_users:register")
            
            if nurse_user.identity_card_picture:
                nurse_user.identity_card_picture.delete(save=False)

            nurse_user.identity_card_picture = identity_card_picture

        
        nurse_user.first_name = first_name
        nurse_user.last_name = last_name 
        nurse_user.display_user_name = user_name
        nurse_user.birthday = gregorian_date
        nurse_user.province = province 
        nurse_user.city = city 
        nurse_user.phone_number = phone_number
        nurse_user.address = address
        nurse_user.sex = sex
        nurse_user.education_level = ed_level_instance
        nurse_user.national_id_number = national_id_number

        # needs the admin approvement 
        nurse_user.is_active = False
        
        try:
            nurse_user.save()
        except Exception:
            messages.error(request, "خطا در تغییر اطلاعات", 'danger')
            return redirect("nurse_users:dashboard")
        
        # new register request to the admin
        registeration_request.status = "in_progress"
        registeration_request.approved = False
        try:
            registeration_request.save()
        except Exception:
            messages.error(request, "خطا در تغییر اطلاعات", 'danger')
            return redirect("nurse_users:dashboard")

        messages.success(request, "اطلاعات شما با موفقیت تغییر کرد", 'success')
        return redirect('nurse_users:dashboard')
    

class UpdateAdditionalView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_nurse:
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_additional_info = nurse_user.nurse_user_additional_info
        except NurseUser.DoesNotExist:
            messages.error(request, "حساب پرستار یافت نشد", 'danger')
            return redirect('home:index')
        
        selected_skills = request.POST.getlist("skills")
        selected_knowledge = request.POST.getlist("knowledge")
        selected_nursing = request.POST.get("modern_nursing")
        is_part_time = request.POST.get('is_part_time') == 'True'

        # Validate the Modern Nursing selection
        modern_nursing_instance = None
        if selected_nursing:
            try:
                modern_nursing_instance = ModernNursing.objects.get(id=selected_nursing)
            except ModernNursing.DoesNotExist:
                modern_nursing_instance = None

        # Validate selected skills using the new Skills model
        valid_skills = Skills.objects.filter(id__in=selected_skills)
        
        # Validate additional knowledge (assuming this model remains unchanged)
        valid_knowledge = AdditionalKnowledg.objects.filter(id__in=selected_knowledge)

        try:
            # Process each selected skill: update NurseSkills and automatically add related NurseSubSkill records
            with transaction.atomic():
                for skill in valid_skills:
                    nurse_skill, created = NurseSkills.objects.get_or_create(
                        nurse=nurse_additional_info,
                        skill=skill,
                    )
                    nurse_skill.save()  # Ensures any side effects are applied

                    # For each subskill under this skill, ensure a NurseSubSkill record exists
                    for subskill in skill.sub_skill.all():
                        NurseSubSkill.objects.get_or_create(
                            nurse=nurse_additional_info,
                            subskill=subskill,
                            nurse_skill=nurse_skill,
                            defaults={'custom_price': subskill.standard_price}
                        )
                
                # Remove any NurseSkills (and their associated NurseSubSkill records by cascade) that are no longer selected
                nurse_additional_info.nurse_skills.exclude(skill__in=valid_skills).delete()

                # Update additional nurse information
                nurse_additional_info.additional_knowledg.set(valid_knowledge)
                nurse_additional_info.modern_nursing = modern_nursing_instance
                nurse_additional_info.part_time = is_part_time
                nurse_additional_info.save()
        except Exception as e:
            # Optionally log the exception for debugging purposes
            messages.error(request, "خطا در تغییر اطلاعات", 'danger')
            return redirect("nurse_users:dashboard")
        
        messages.success(request, "اطلاعات شما با موفقیت تغییر کرد", 'success')
        return redirect('nurse_users:dashboard')


class UpdateWorkingHoursView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):
        try: 
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_additional_info = nurse_user.nurse_user_additional_info
        except Exception:
            messages.error(request, "حساب پرستار یافت نشد", 'danger')
            return redirect('home:index')
        
        working_hours_form = WorkingHoursForm(request.POST)

        if working_hours_form.is_valid():
            if WorkingHours.objects.filter(nurse_additional=nurse_additional_info).count() < 10:
                # save the working hour 
                working_hour = working_hours_form.save(commit=False) # Don't save yet
                working_hour.nurse_additional = nurse_additional_info
                working_hour.save()

                messages.success(request, "اطلاعات شما با موفقیت تغییر کرد", 'success')
                return redirect("nurse_users:dashboard")
            else:
                messages.error(request, "شما نمیتوانید بیشتر از ۱۰ مورد ایجاد کنید", 'danger')
                return redirect("nurse_users:dashboard")
        else:
            messages.error(request, "در وارد کردن اطلاعات دقت کنید", 'danger')
            return redirect("nurse_users:dashboard")


class DeleteWorkingHours(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):
        if request.POST.get('_method') == 'DELETE':
            try: 
                nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
                nurse_additional_info = nurse_user.nurse_user_additional_info
            except Exception:
                messages.error(request, "حساب پرستار یافت نشد", 'danger')
                return redirect('home:index')
            
            user_working_hours = nurse_additional_info.working_hours.all()

            if user_working_hours.exists():
                user_working_hours.delete()
                messages.success(request, "ساعات کاری شما با موفقیت حذف شدند", 'success')
            else:
                messages.error(request, "ساعت کاری برای حذف شدن وجود ندارد", 'danger')
            
            return redirect("nurse_users:dashboard")
        else:
            return HttpResponseNotAllowed(['POST'])


class UpdateWorkExperienceView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):
        try: 
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_additional_info = nurse_user.nurse_user_additional_info
        except Exception:
            messages.error(request, "حساب پرستار یافت نشد", 'danger')
            return redirect('home:index')
        

        work_experience_title = request.POST.get('work_experience_title')
        start_work = request.POST.get('start_work')
        end_work = request.POST.get('end_work')

        if not is_valid_name(work_experience_title):
            messages.error(request, "نام مرکز وارد شده را بررسی کنید(نام مرکز باید فارسی باشد)", 'danger')
            return redirect("nurse_users:dashboard")
        
        try: 
            gregorian_date_start = jalali_convertor(start_work) 
        except Exception:
            messages.error(request, "تاریخ شروع وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")  
        
        try: 
            gregorian_date_end = jalali_convertor(end_work) 
        except Exception:
            messages.error(request, "تاریخ پایان وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")  
        
        if not is_valid_work_experience(gregorian_date_start, gregorian_date_end):
            messages.error(request, "تاریخ های وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")
        
        if WorkExperience.objects.filter(nurse_additional_info=nurse_additional_info).count() > 10:
            messages.error(request, "محدودیت در تعداد سوابق تعریف شده", 'danger')
            return redirect("nurse_users:dashboard")

        try:
            nurse_additional_info.work_experience.create(title=work_experience_title, \
                                                        start_work=gregorian_date_start, \
                                                            end_work=gregorian_date_end)
        except Exception:
            messages.error(request, "خطا در تغییر اطلاعات", 'danger')
            return redirect("nurse_users:dashboard")

        messages.success(request, "سابقه شغلی شما ایجاد شد", 'success')
        return redirect('nurse_users:dashboard')
        

class DeleteWorkExperience(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):
        if request.POST.get('_method') == 'DELETE':
            try: 
                nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
                nurse_additional_info = nurse_user.nurse_user_additional_info
            except Exception:
                messages.error(request, "حساب پرستار یافت نشد", 'danger')
                return redirect('home:index')
            
            user_working_experience = nurse_additional_info.work_experience.all()

            if user_working_experience.exists():
                user_working_experience.delete()
                messages.success(request, " سوابق کاری شما با موفقیت حذف شدند", 'success')
            else:
                messages.error(request, "سوابق کاری برای حذف شدن وجود ندارد", 'danger')
            
            return redirect("nurse_users:dashboard")
        else:
            return HttpResponseNotAllowed(['POST'])
        
        
class UpdateNurseLocationView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_additional_info = nurse_user.nurse_user_additional_info
        except Exception:
                messages.error(request, "حساب پرستار یافت نشد", 'danger')
                return redirect('home:index')

        location_form = NurseLocationForm(request.POST)
        if location_form.is_valid():
            location_data = location_form.cleaned_data['location']

            if not is_location_within_iran(location_data):
                messages.error(request, "موقعیت جغرافیایی خارج از ایران پشتیبانی نمیشود", 'danger')
                return redirect("nurse_users:dashboard")

            if nurse_additional_info.nurse_location:
                # Update existing location
                nurse_additional_info.nurse_location.location = location_data
                nurse_additional_info.nurse_location.save()
            else:
                # Create new location
                new_location = location_form.save()
                nurse_additional_info.nurse_location = new_location
                nurse_additional_info.save()

            messages.success(request, "موقعیت شما با موفقیت ذخیره شد", 'success')
            return redirect('nurse_users:dashboard')
        
        messages.error(request, "خطا در تغییر اطلاعات", 'danger')
        return redirect("nurse_users:dashboard")
        

# class UpdateNurseSubSkillPrice(View):
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated and request.user.is_nurse:
#             return super().dispatch(request, *args, **kwargs)
#         messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
#         return redirect('home:index')
    
#     def post(self, request):
#         try:
#             nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
#             nurse_additional_info = nurse_user.nurse_user_additional_info
#         except NurseUser.DoesNotExist:
#             messages.error(request, "حساب پرستار یافت نشد", 'danger')
#             return redirect('home:index')
        
#         # Expecting the form to send NurseSubSkill IDs
#         subskill_ids = request.POST.getlist("nurse_subskill_id")
#         valid_subskills = NurseSubSkill.objects.filter(nurse=nurse_additional_info, id__in=subskill_ids)

#         for nurse_subskill in valid_subskills:
#             try:
#                 # Retrieve the new price input; form field name is like custom_price_123 where 123 is nurse_subskill.id
#                 custom_price_input = request.POST.get(f"custom_price_{nurse_subskill.id}", "").strip()
#                 custom_price = int(custom_price_input)

#                 if not is_valid_price(custom_price):
#                     messages.error(request, "به قیمت وارد شده خود دقت کنید", 'danger')
#                     return redirect("nurse_users:dashboard")
                
#                 # Ensure the new price is not lower than the SubSkill's standard price
#                 if custom_price < nurse_subskill.subskill.standard_price:
#                     messages.error(request, "به قیمت وارد شده خود دقت کنید؛ نباید پایین‌تر از تعرفه استاندارد باشد", 'danger')
#                     return redirect("nurse_users:dashboard")
                
#                 nurse_subskill.custom_price = custom_price
#                 nurse_subskill.save()
#             except Exception as e:
#                 messages.error(request, "مشکل در ثبت قیمت", 'danger')
#                 return redirect("nurse_users:dashboard")
            
#         messages.success(request, "قیمت جدید با موفقیت ذخیره شد", 'success')    
#         return redirect('nurse_users:dashboard')


class UpdateDescriptionView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری پرستار خود حضور ندارید", 'danger')
        return redirect('home:index')
    
    def post(self, request):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_additional_info = nurse_user.nurse_user_additional_info
        except Exception:
            messages.error(request, "حساب پرستار یافت نشد", 'danger')
            return redirect('home:index')
        
        nurse_description = request.POST.get('nurse_description')

        if not is_valid_description(nurse_description):
            messages.error(request, "توضیحات وارد شده خود را بررسی کنید", 'danger')
            return redirect("nurse_users:dashboard")
        
        nurse_additional_info.description = nurse_description

        try:
            nurse_additional_info.save()
            messages.success(request, "توضیحات با موفقیت ثبت شد", 'success') 
        except Exception:
            messages.error(request, "خطا در ثبت اطلاعات", 'danger')
            return redirect("nurse_users:dashboard")
        
        return redirect("nurse_users:dashboard")