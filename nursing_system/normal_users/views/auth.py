from django.shortcuts import render, redirect
from extensions.auth_utils import is_valid_phone_number, is_valid_password_login, send_otp_code, \
    is_valid_otp, is_valid_password_reset
from django.contrib.auth import authenticate, login, logout
from normal_users.models import OtpCodeModel
from django.contrib.auth import get_user_model
from normal_users.tasks import send_otp_sms
from django.contrib import messages
from django.views import View
import random

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

User = get_user_model()

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='post')
class LoginView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render (request, 'normal_users/login.html')
    

    def post(self, request):
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")

        if not is_valid_phone_number(phone_number):
            messages.error(request, "شماره موبایل خود را بررسی کنید", 'danger')
            return redirect("normal_users:login")
        
        if not is_valid_password_login(password):
            messages.error(request, "در وارد کردن رمز خود دقت کنید", 'danger')
            return redirect("normal_users:login")
        
        user = authenticate(phone_number=phone_number, password=password)
        if user is not None:
            login(request, user)
            messages.success(request , 'شما وارد حساب خود شدید' , 'success')
            return redirect("home:index")
        else: 
            messages.error(request, "نام کاربری یا رمز عبور اشتباه است", 'danger')
            return redirect("normal_users:login")


class LogoutView(View):
    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.success(request , 'شما از حساب خود خارج شدید' , 'danger')
        else: 
            messages.warning(request, 'شما وارد حساب خود نشده‌اید', 'warning')

        return redirect('home:index')
    

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='post')
class PasswordResetView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, 'normal_users/password_reset.html')
    
    def post(self, request):
        phone_number = phone_number = request.POST.get("phone_number")

        if not is_valid_phone_number(phone_number):
            messages.error(request, "شماره موبایل خود را بررسی کنید", 'danger')
            return redirect("normal_users:password_reset")
        
        if not User.objects.filter(phone_number=phone_number).exists():
            request.session['user_password_reset'] = {
            'phone_number':'',
            'otp_verified':False,
            'process':False
            }
            messages.success(request, "پیام تایید هویت به شماره شما ارسال شد", 'success')
            return redirect('normal_users:password_reset_vertify')
        
        otp_instance = OtpCodeModel.objects.filter(phone_number=phone_number).first()

        if otp_instance:
            messages.error(request, "کد تایید قبلا ارسال شده است. دوباره تلاش کنید.", 'danger')
            otp_instance.delete()  # Delete the existing OTP
            return redirect("normal_users:password_reset")

        random_code = random.randint(1000, 9999)
        try:
            # send_otp_code(phone_number, random_code)

            # this new one is a celery task
            send_otp_sms.delay(phone_number, random_code)
        except Exception:
            messages.error(request, "مشکل در ارسال کد", 'danger')
            return redirect("normal_users:password_reset")
        
        OtpCodeModel.objects.create(phone_number=phone_number, otp=random_code)
        request.session['user_password_reset'] = {
            'phone_number':phone_number,
            'otp_verified':False,
            'process':True
        }
        messages.success(request, "پیام تایید هویت به شماره شما ارسال شد", 'success')
        return redirect('normal_users:password_reset_vertify')
    

@method_decorator(ratelimit(key='ip', rate='3/m', block=True), name='post')
class PasswordResetVertifyView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        if 'user_password_reset' not in request.session:
            messages.error(request, "لطفا ابتدا فرم بازیابی رمز را تکمیل کنید.", 'danger')
            return redirect("normal_users:password_reset")
        
        return render(request, 'normal_users/password_reset_vertify.html')
    
    def post(self, request):
        if 'user_password_reset' not in request.session:
            messages.error(request, "لطفا ابتدا فرم بازیابی رمز را تکمیل کنید.", 'danger')
            return redirect("normal_users:password_reset")
        
        if not request.session.get('user_password_reset', {}).get('process', False):
            messages.error(request, "کد تایید نادرست.", 'danger')
            return redirect("normal_users:password_reset_vertify")
        
        user_input = request.POST.get("otp_code")
        if not is_valid_otp(user_input):
            messages.error(request, "کد تایید نادرست.", 'danger')
            return redirect("normal_users:password_reset_vertify")
        
        user_input = int(user_input)
        user_session = request.session['user_password_reset']

        try:
            code_instance = OtpCodeModel.objects.get(phone_number=user_session['phone_number'])
        except OtpCodeModel.DoesNotExist:
            messages.error(request, "کد تایید برای این شماره موبایل یافت نشد.", 'danger')
            return redirect("normal_users:password_reset")
        
        if user_input == code_instance.otp: 
            if code_instance.is_expired():
                code_instance.delete()
                messages.error(request, "زمان شما به اتمام رسید", 'danger')
                del request.session['user_password_reset']
                return redirect('normal_users:password_reset')
            
            # If OTP is valid and not expired, proceed to set password view
            code_instance.delete()
            request.session['user_password_reset']['otp_verified'] = True
            request.session.modified = True
            messages.success(request, "کد تایید درست است. برای ادامه رمز خود را تعیین کنید.", 'success')
            return redirect('normal_users:password_reset_vertify_set')
        else:
            # Invalid OTP code entered
            messages.error(request, "کد تایید نادرست.", 'danger')
            return redirect("normal_users:password_reset_vertify")
        

@method_decorator(ratelimit(key='ip', rate='5/m', block=True), name='post')
class PasswordResetVertifySetView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حساب کاربری خود حضور دارید", 'danger')
            return redirect('home:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        if not request.session.get('user_password_reset', {}).get('otp_verified', False):
            messages.error(request, "لطفا ابتدا فرم بازیابی رمز را تکمیل کنید", 'danger')
            return redirect("normal_users:password_reset")

        return render(request, 'normal_users/password_reset_vertify_set.html')
    
    def post(self, request):
        if not request.session.get('user_password_reset', {}).get('otp_verified', False):
            messages.error(request, "1لطفا ابتدا فرم بازیابی رمز را تکمیل کنید", 'danger')
            return redirect("normal_users:password_reset")
        
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirtm_password')
        user_session = request.session['user_password_reset']

        if not is_valid_password_reset(password1, password2):
            messages.error(request, "در انتخاب رمز خود دقت کنید", 'danger')
            return redirect("normal_users:password_reset_vertify_set")
        
        try:
            the_user = User.objects.get(phone_number=user_session['phone_number'])
            the_user.set_password(password1)
            the_user.save()
        except Exception:
            del request.session['user_password_reset']
            messages.error(request, "خطایی رخ داده. پس از مدتی دوباره تلاش کنید.", 'danger')
            return redirect("normal_users:password_reset")
        
        del request.session['user_password_reset']
        messages.success(request, "رمز شما تغییر کرد", 'success')
        return redirect('home:index')
