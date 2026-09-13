from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from extensions.auth_utils import is_valid_phone_number, is_valid_user_name, is_valid_otp, \
      send_otp_code, is_valid_password
from django.db import IntegrityError
from normal_users.models import OtpCodeModel
from django.contrib import messages
from django.views import View
from django.shortcuts import render, redirect
from extensions.auth_utils_nurse import is_valid_province
from normal_users.tasks import send_otp_sms
import random

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

User = get_user_model()

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='post')
class UserRegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, 'normal_users/register.html')
    
    def post(self, request):
        phone_number = request.POST.get('phone_number')
        user_name = request.POST.get('user_name')
        province = request.POST.get('province')
        print(province)
        
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "شماره موبایل تکراری است", 'danger')
            return redirect("normal_users:register")

        if not is_valid_phone_number(phone_number):
            messages.error(request, "شماره موبایل خود را بررسی کنید", 'danger')
            return redirect("normal_users:register")
        
        if not is_valid_user_name(user_name):
            messages.error(request, "نام کاربری خود را بررسی کنید نباید طول آن کمتر ۴ حرف باشد", 'danger')
            return redirect("normal_users:register")
        
        if not is_valid_province(province):
            messages.error(request, "استان وارد شده را بررسی کنید", 'danger')
            return redirect("normal_users:register")

        
        otp_instance = OtpCodeModel.objects.filter(phone_number=phone_number).first()
            
        if otp_instance:
            messages.error(request, "کد تایید قبلا ارسال شده است. دوباره تلاش کنید.", 'danger')
            otp_instance.delete()  # Delete the existing OTP
            return redirect("normal_users:register")
        
        random_code = random.randint(1000, 9999)
        try:
            # send_otp_code(phone_number, random_code)
            
            # this new one is a celery task
            send_otp_sms.delay(phone_number, random_code)
        except Exception:
            messages.error(request, "مشکل در ارسال کد", 'danger')
            return redirect("normal_users:register")
        
        OtpCodeModel.objects.create(phone_number=phone_number, otp=random_code)
        request.session['user_registration_info'] = {
            'phone_number':phone_number,
            'user_name':user_name,
            'province':province,
            'otp_verified':False,
        }
        messages.success(request, "کد را برای شما از طریق پیامک ارسال کردیم", 'success')
        return redirect("normal_users:register_vertify")
    

@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='post')
class UserRegisterVertifyView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        if 'user_registration_info' not in request.session:
            messages.error(request, "لطفا ابتدا فرم ثبت‌نام را تکمیل کنید.", 'danger')
            return redirect("normal_users:register")
        
        return render(request, 'normal_users/register_vertify.html')
    
    def post(self, request):
        if 'user_registration_info' not in request.session:
            messages.error(request, "لطفا ابتدا فرم ثبت‌نام را تکمیل کنید.", 'danger')
            return redirect("normal_users:register")
        
        user_input = request.POST.get("otp_code")
        if not is_valid_otp(user_input):
            messages.error(request, "کد تایید نادرست.", 'danger')
            return redirect("normal_users:register_vertify")
        
        user_input = int(user_input)
        user_session = request.session['user_registration_info']

        try:
            code_instance = OtpCodeModel.objects.get(phone_number=user_session['phone_number'])
        except OtpCodeModel.DoesNotExist:
            del request.session['user_registration_info']
            messages.error(request, "کد تایید برای این شماره موبایل یافت نشد.", 'danger')
            return redirect("normal_users:register")

        if user_input == code_instance.otp: 
            if code_instance.is_expired():
                code_instance.delete()
                messages.error(request, "زمان شما به اتمام رسید", 'danger')
                del request.session['user_registration_info']
                return redirect('normal_users:register')
            
            # If OTP is valid and not expired, proceed to set password view
            code_instance.delete()
            request.session['user_registration_info']['otp_verified'] = True
            request.session.modified = True
            messages.success(request, "کد تایید درست است. برای ادامه رمز خود را وارد کنید.", 'success')
            return redirect('normal_users:register_setpass')
        else:
            # Invalid OTP code entered
            messages.error(request, "کد تایید اشتباه است. لطفا دوباره تلاش کنید.", 'danger')
            return redirect("normal_users:register_vertify")
                

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='post')
class UserRegisterSetPass(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        if not request.session.get('user_registration_info', {}).get('otp_verified', False):
            messages.error(request, "لطفا ابتدا فرم ثبت‌نام را تکمیل کنید", 'danger')
            return redirect("normal_users:register")

        return render(request, 'normal_users/register_setpass.html')
        
    
    def post(self, request):
        if not request.session.get('user_registration_info', {}).get('otp_verified', False):
            messages.error(request, "1لطفا ابتدا فرم ثبت‌نام را تکمیل کنید", 'danger')
            return redirect("normal_users:register")
        
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirtm_password')
        user_session = request.session['user_registration_info']
        user_name = user_session['user_name']

        if not is_valid_password(password1, password2, user_name):
            messages.error(request, "در انتخاب رمز خود دقت کنید", 'danger')
            return redirect("normal_users:register_setpass")
        
        try:
            user = User.objects.create_user(phone_number=user_session['phone_number'], \
                                            user_name=user_session['user_name'], password=password1, \
                                                province=user_session['province'])
        except IntegrityError:
            # Handle duplicate phone number or other DB integrity issues
            del request.session['user_registration_info']
            messages.error(request, "A user with this phone number already exists.", 'danger')
            return redirect('normal_users:register')
        except ValueError as e:
            # Handle missing or invalid data
            del request.session['user_registration_info']
            messages.error(request, "An unexpected error occurred. Please try again later.", 'danger')
            return redirect('normal_users:register')
        except Exception as e:
            # Catch any other unexpected errors
            del request.session['user_registration_info']
            messages.error(request, "An unexpected error occurred. Please try again later.", 'danger')
            return redirect('normal_users:register')
        
        del request.session['user_registration_info']
        messages.success(request, "حساب کاربری شما ایجاد شد", 'success')

        #  login after register 

        the_user = authenticate(username=user_session['phone_number'], password=password1)
        if the_user is not None:
            login(request, user)
            return redirect("home:index")
        else:
            messages.error(request, "مشکل در ورود به حساب", 'danger')
            return redirect('home:index')