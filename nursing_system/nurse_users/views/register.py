from django.shortcuts import render, redirect
from extensions.auth_utils import is_valid_user_name, is_valid_phone_number, send_otp_code, \
      is_valid_otp, is_valid_password
from extensions.auth_utils_nurse import is_valid_name, is_valid_image, is_valid_sex, \
    delete_temp_file, get_unique_filename, get_unique_filename2, is_valid_address, is_valid_province, \
    check_national_id_number, return_redirect_nurse
from extensions.auth_services import is_valid_display_name
from django.db import transaction
from services.models import NurseWallet
from django.contrib.auth import authenticate, login
from extensions.auth_utils_nurse import jalali_convertor
from django.contrib.auth import get_user_model
from django.contrib import messages
from normal_users.models import OtpCodeModel
from django.db import IntegrityError
from nurse_users.models import EducationLevel, NurseUser, RegistrationRequest, NurseUserAdditionalInfo
from normal_users.tasks import send_otp_sms
from django.views import View
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from extensions.auth_utils_nurse import get_s3_client
import random
import shutil
import os

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

# Create your views here.


# Temporary File Storage
fs = FileSystemStorage(location=settings.TEMP_UPLOAD_DIR)

User = get_user_model()

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='post')
class NurseAlreadyRegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "خطا در احراز هویت صفحه تغییر به پرستار", 'danger')
        return redirect('home:index')
        
    
    def get(self, request):
        context = {
            'education_levels': EducationLevel.objects.all(),
        }
        return render(request, 'nurse_users/register/register.html', context)
    
    def post(self, request):
        input_data = request.POST

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_name = request.POST.get('user_name')
        birthday = request.POST.get('birthday')
        province = request.POST.get('province')
        city = request.POST.get('city')
        national_id_number = request.POST.get('national_id_number')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        ministry_proof_picture = request.FILES.get('ministry_proof_picture')
        identity_card_picture = request.FILES.get('identity_card_picture')
        profile_picture = request.FILES.get('profile_picture')
        sex = request.POST.get('sex')
        education_level_id = request.POST.get('education_level')
        is_legal_entity = request.POST.get('is_legal_entity')


        if NurseUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "شماره موبایل تکراری است", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_name(first_name):
            messages.error(request, "نام وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_name(last_name):
            messages.error(request, "نام خانوادگی وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        try: 
            gregorian_date = jalali_convertor(birthday) 
        except Exception:
            messages.error(request, "تاریخ تولد وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_province(province):
            messages.error(request, "استان وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_name(city):
            messages.error(request, "شهر وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_phone_number(phone_number):
            messages.error(request, "شماره موبایل وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_address(address):
            messages.error(request, "آدرس وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_image(ministry_proof_picture):
            messages.error(request, "گواهی تایید وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_image(profile_picture):
            messages.error(request, "عکس پرستار وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_sex(sex):
            messages.error(request, "جنیست وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        try:
            ed_level_instance = EducationLevel.objects.get(id=education_level_id)
        except Exception:
            messages.error(request, "مدرک تحصیلی وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        is_valid_user_name, message = is_valid_display_name(user_name)
        if not is_valid_user_name:
            messages.error(request, f"{message}", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not check_national_id_number(national_id_number):
            messages.error(request, "کد ملی وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if not is_valid_image(identity_card_picture):
            messages.error(request, "عکس کارت ملی وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register.html')
        
        if is_legal_entity == "on":
            is_legal_entity = True
        else:
            is_legal_entity = False
        
        try:
            with transaction.atomic():
                the_user = request.user
                the_user.is_nurse = True
                the_user.save()
                nurse_user = NurseUser.objects.create(first_name=first_name, last_name=last_name,\
                                            birthday=gregorian_date,  province=province, \
                                            city=city, phone_number=phone_number, \
                                            national_id_number=national_id_number, \
                                                ministry_proof_picture= ministry_proof_picture, \
                                                    profile_picture=profile_picture, \
                                                    identity_card_picture=identity_card_picture, \
                                                            education_level=ed_level_instance, \
                                                            sex=sex, custom_user_id=the_user.user_id, \
                                                            address=address, display_user_name=user_name, \
                                                            is_legal_entity=is_legal_entity
                                            )
                nurse_add = NurseUserAdditionalInfo.objects.create(nurse=nurse_user)
                
                reg_info = RegistrationRequest.objects.create(nurse=nurse_user)
                wallet0 = NurseWallet.objects.create(nurse_id=nurse_user.custom_user_id)

        except Exception:
            messages.error(request, "خطا در ثبت نام", 'danger')
            return redirect("nurse_users:register")
        
        messages.success(request, "درخواست شما برای ایجاد حساب کاربری پرستار ارسال شد", 'success')
        return redirect('home:index')
        

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='dispatch')
class NurseNewRegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        context = {
            'education_levels': EducationLevel.objects.all(),
        }
        return render(request, 'nurse_users/register/register2.html', context)
    
    def post(self, request):
        input_data = request.POST

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_name = request.POST.get('user_name')
        birthday = request.POST.get('birthday')
        province = request.POST.get('province')
        city = request.POST.get('city')
        national_id_number = request.POST.get('national_id_number')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        sex = request.POST.get('sex')
        education_level_id = request.POST.get('education_level')
        is_legal_entity = request.POST.get('is_legal_entity')

        if NurseUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "شماره موبایل تکراری است", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        if not is_valid_name(first_name):
            messages.error(request, "نام وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        if not is_valid_name(last_name):
            messages.error(request, "نام خانوادگی وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        try: 
            gregorian_date = jalali_convertor(birthday) 
        except Exception:
            messages.error(request, "تاریخ تولد وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        if not is_valid_province(province):
            messages.error(request, "استان وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        if not is_valid_name(city):
            messages.error(request, "شهر وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        if not is_valid_phone_number(phone_number):
            messages.error(request, "شماره موبایل وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        if not is_valid_address(address):
            messages.error(request, "آدرس وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        if not is_valid_sex(sex):
            messages.error(request, "جنیست وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        try:
            ed_level_instance = EducationLevel.objects.get(id=education_level_id)
        except Exception:
            messages.error(request, "مدرک تحصیلی وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        is_valid_user_name, message = is_valid_display_name(user_name)
        if not is_valid_user_name:
            messages.error(request, f"{message}", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        if not check_national_id_number(national_id_number):
            messages.error(request, "کد ملی وارد شده را بررسی کنید", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        

        if is_legal_entity == "on":
            is_legal_entity = True
        else:
            is_legal_entity = False
        
        
        # the nurse validations start
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "شماره موبایل تکراری است", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        otp_instance = OtpCodeModel.objects.filter(phone_number=phone_number).first()   
        if otp_instance:
            messages.error(request, "کد تایید قبلا ارسال شده است. دوباره تلاش کنید.", 'danger')
            otp_instance.delete()  # Delete the existing OTP
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')

        random_code = random.randint(1000, 9999)
        try:
            # send_otp_code(phone_number, random_code)
            
            # this new one is a celery task
            send_otp_sms.delay(phone_number, random_code)
        except Exception:
            messages.error(request, "مشکل در ارسال کد", 'danger')
            return return_redirect_nurse(request, input_data, 'nurse_users/register/register2.html')
        
        OtpCodeModel.objects.create(phone_number=phone_number, otp=random_code)


        request.session['nurse_registration_info'] = {
            'phone_number':phone_number,
            'user_name':user_name,
            'otp_verified':False,

            # nurse info
            'first_name':first_name,
            'last_name':last_name,
            'birthday':birthday,
            'province':province,
            'city':city,
            'address':address,
            'sex':sex,
            'national_id_number':national_id_number,
            'education_level_id':education_level_id,
            'is_legal_entity':is_legal_entity,
            'new_nurse':True

        }
        messages.success(request, "کد تایید را برای شما از طریق پیامک ارسال کردیم", 'success')
        return redirect("nurse_users:register_vertify")
        

@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='dispatch')
class NurseRegisterVertifyView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        if 'nurse_registration_info' not in request.session:
            messages.error(request, "لطفا ابتدا فرم ثبت‌نام را تکمیل کنید.", 'danger')
            return redirect("nurse_users:new_register")
        
        return render(request, 'nurse_users/register/register_vertify.html')
    
    def post(self, request): 
        if 'nurse_registration_info' not in request.session:
            messages.error(request, "لطفا ابتدا فرم ثبت‌نام را تکمیل کنید.", 'danger')
            return redirect("nurse_users:new_register")
        
        user_input = request.POST.get("otp_code")
        if not is_valid_otp(user_input):
            messages.error(request, "کد تایید نادرست.", 'danger')
            return redirect("nurse_users:register_vertify")
        
        user_input = int(user_input)
        user_session = request.session['nurse_registration_info']

        try:
            code_instance = OtpCodeModel.objects.get(phone_number=user_session['phone_number'])
        except OtpCodeModel.DoesNotExist:
            del request.session['nurse_registration_info']
            messages.error(request, "کد تایید برای این شماره موبایل یافت نشد.", 'danger')
            return redirect("nurse_users:new_register")
        
        if user_input == code_instance.otp: 
            if code_instance.is_expired():
                code_instance.delete()
                messages.error(request, "زمان شما به اتمام رسید", 'danger')
                del request.session['nurse_registration_info']
                return redirect('nurse_users:new_register')
            
            # If OTP is valid and not expired, proceed to set password view
            code_instance.delete()
            request.session['nurse_registration_info']['otp_verified'] = True
            request.session.modified = True
            messages.success(request, "کد تایید درست است. برای ادامه رمز خود را وارد کنید.", 'success')
            return redirect('nurse_users:register_setpass')
        else:
            # Invalid OTP code entered
            messages.error(request, "کد تایید اشتباه است. لطفا دوباره تلاش کنید.", 'danger')
            return redirect("nurse_users:register_vertify")
        

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='dispatch')
class NurseRegisterSetPass(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        if not request.session.get('nurse_registration_info', {}).get('otp_verified', False):
            messages.error(request, "لطفا ابتدا فرم ثبت‌نام را تکمیل کنید", 'danger')
            return redirect("nurse_users:register")
        
        return render(request, 'nurse_users/register/register_setpass.html')
    
    def post(self, request):
        if not request.session.get('nurse_registration_info', {}).get('otp_verified', False):
            messages.error(request, "1لطفا ابتدا فرم ثبت‌نام را تکمیل کنید", 'danger')
            return redirect("nurse_users:register")
        
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirtm_password')
        ministry_proof_picture = request.FILES.get('ministry_proof_picture')
        identity_card_picture = request.FILES.get('identity_card_picture')
        profile_picture = request.FILES.get('profile_picture')
        user_session = request.session['nurse_registration_info']
        user_name = user_session['user_name']

        if not is_valid_password(password1, password2, user_name):
            messages.error(request, "در انتخاب رمز خود دقت کنید", 'danger')
            return redirect("nurse_users:register_setpass")
        
        if not is_valid_image(ministry_proof_picture):
            messages.error(request, "گواهی تایید وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:register_setpass")
        
        if not is_valid_image(profile_picture):
            messages.error(request, "عکس پرستار وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:register_setpass")
        
        if not is_valid_image(identity_card_picture):
            messages.error(request, "عکس کارت ملی وارد شده را بررسی کنید", 'danger')
            return redirect("nurse_users:register_setpass")
        
        try:
            user = User.objects.create_user(phone_number=user_session['phone_number'], \
                                            user_name=user_session['user_name'], password=password1, \
                                                is_nurse=True, province=user_session['province'])
        except IntegrityError:
            # Handle duplicate phone number or other DB integrity issues
            del request.session['nurse_registration_info']
            messages.error(request, "A user with this phone number already exists.", 'danger')
            return redirect('nurse_users:new_register')
        except ValueError as e:
            # Handle missing or invalid data
            del request.session['nurse_registration_info']
            messages.error(request, "An unexpected error occurred. Please try again later.", 'danger')
            return redirect('nurse_users:new_register')
        except Exception as e:
            # Catch any other unexpected errors
            del request.session['nurse_registration_info']
            messages.error(request, "An unexpected error occurred. Please try again later.", 'danger')
            return redirect('nurse_users:new_register')
        
        messages.success(request, "حساب کاربری شما ایجاد شد", 'success')

        #  login after register 
        the_user = authenticate(username=user_session['phone_number'], password=password1)
        if the_user is not None:
            login(request, user)
        else:
            del request.session['nurse_registration_info']
            messages.error(request, "مشکل در ورود به حساب", 'danger')
            return redirect('home:index')
        
        # create nurse after login
        the_user = request.user

        #fix the jalali date to store
        gregorian_date = jalali_convertor(user_session['birthday'])

        # get the education level
        ed_level_instance = EducationLevel.objects.get(id=user_session['education_level_id'])


        try:
            with transaction.atomic():
                nurse_user = NurseUser.objects.create(first_name=user_session['first_name'], last_name=user_session['last_name'],\
                                            birthday=gregorian_date,  province=user_session['province'], \
                                            city=user_session['city'], phone_number=user_session['phone_number'], \
                                                ministry_proof_picture=ministry_proof_picture, \
                                                    profile_picture=profile_picture, \
                                                    identity_card_picture = identity_card_picture, \
                                                            education_level=ed_level_instance, \
                                                            sex=user_session['sex'], custom_user_id=the_user.user_id, \
                                                            address=user_session['address'], \
                                                            display_user_name=user_session['user_name'], \
                                                            national_id_number=user_session['national_id_number'],
                                                            is_legal_entity=user_session['is_legal_entity']
                                        )
                ad_info = NurseUserAdditionalInfo.objects.create(nurse=nurse_user)
                reg_request = RegistrationRequest.objects.create(nurse=nurse_user)
                wallet0 = NurseWallet.objects.create(nurse_id=nurse_user.custom_user_id)

        except Exception:
            messages.error(request, "مشکل در ثبت پرستار", 'danger')
            return redirect('home:index')
 
        messages.success(request, "درخواست شما برای ایجاد حساب کاربری پرستار ارسال شد", 'success')
        request.session.pop('nurse_registration_info', None)
        return redirect("home:index")

