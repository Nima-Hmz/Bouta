from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from nurse_users.models import NurseUser
from services.models import NurseWallet, BankInfoRequest, NursePayRequest, WalletTransaction
from django.db import transaction
from extensions.auth_services import back_to_previous_page, is_valid_bank_info, is_valid_money_info
from django.views import View

class NurseWalletView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def get(self, request):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_wallet = NurseWallet.objects.get(nurse_id=nurse_user.custom_user_id)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return back_to_previous_page(request)
        
        pay_requests = NursePayRequest.objects.filter(wallet=nurse_wallet)[:3]
        
        wallet_transactions = WalletTransaction.objects.filter(wallet=nurse_wallet)
        paginator = Paginator(wallet_transactions, 6)  

        page = request.GET.get('page')

        try:
            w_transactions = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver the first page.
            w_transactions = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g., 9999), deliver last page of results.
            w_transactions = paginator.page(paginator.num_pages)


        
        context = {
            'nurse_core':nurse_user,
            'nurse_wallet':nurse_wallet,
            'bank_info_request':nurse_wallet.bank_info_requests.first(),
            'w_transactions':w_transactions,
            'pay_requests':pay_requests,
        }
        return render(request, 'nurse_users/wallet/wallet.html', context)
    

class NurseBankInfoInputView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    
    def post(self, request):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_wallet = NurseWallet.objects.get(nurse_id=nurse_user.custom_user_id)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return back_to_previous_page(request)

        latest_request = nurse_wallet.bank_info_requests.first()
        bank_info = request.POST.get('bank_info_request')

        if not is_valid_bank_info(bank_info):
            messages.error(request, "اطلاعات وارد شده خود را بررسی کنید", 'danger')
            return back_to_previous_page(request)
        
        if bank_info == nurse_wallet.bank_info:
            messages.error(request, "اطلاعات تکراری است", 'danger')
            return back_to_previous_page(request)

        if latest_request is not None:
            if latest_request.status == 'pending':
                try:
                    with transaction.atomic():
                        latest_request.bank_info = bank_info
                        latest_request.save()
                        nurse_wallet.bank_info = bank_info
                        nurse_wallet.valid_bank_info = False
                        nurse_wallet.save()
                        messages.success(request, "اطلاعات شما ثبت و در حال بررسی است", 'success')
                        return redirect('nurse_users:nurse_wallet')
                except Exception:
                    messages.error(request, "خطا در تغییر اطلاعات کیف پول", 'danger')
                    return back_to_previous_page(request)

        try:
            with transaction.atomic():
                BankInfoRequest.objects.create(wallet=nurse_wallet, bank_info=bank_info)
                nurse_wallet.bank_info = bank_info
                nurse_wallet.valid_bank_info = False
                nurse_wallet.save()
                messages.success(request, "اطلاعات شما ثبت و در حال بررسی است", 'success')
        except Exception:
            messages.error(request, "خطا در تغییر اطلاعات کیف پول", 'danger')
            return back_to_previous_page(request)
        
        return redirect('nurse_users:nurse_wallet')
    

class NursePayView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_nurse:
                return super().dispatch(request, *args, **kwargs)
            
        messages.error(request, "شما در حساب کاربری خود حضور ندارید", 'danger')
        return back_to_previous_page(request)
    

    def post(self, request):
        try:
            nurse_user = NurseUser.objects.get(custom_user_id=request.user.user_id)
            nurse_wallet = NurseWallet.objects.get(nurse_id=nurse_user.custom_user_id)
        except Exception:
            messages.error(request, "خطا در دریافت اطلاعات پرستار", 'danger')
            return back_to_previous_page(request)
        
        if not nurse_wallet.bank_info:
            messages.error(request, "اطلاعات شماره شبا شما در سامانه یافت نشد", 'danger')
            return back_to_previous_page(request)
        
        if not nurse_wallet.valid_bank_info:
            messages.error(request, "اطلاعات شماره شبا شما در سامانه تایید نشده است", 'danger')
            return back_to_previous_page(request)
        
        if NursePayRequest.objects.filter(nurse=nurse_user.custom_user_id, status='pending').exists():
            messages.error(request, "در حال حاضر شما یک درخواست در حال انتظار ثبت شده دارید", 'danger')
            return back_to_previous_page(request)
        
        money_info = request.POST.get('money_info')
        if not is_valid_money_info(money_info):
            messages.error(request, "به ورودی خود دفت کنید(نباید بالا تر از ۱۰ میلیون و پایین تر از ۲۰۰ هزار تومان باشد)", 'danger')
            return back_to_previous_page(request)
        
        money_info = int(money_info)
        if money_info > nurse_wallet.balance:
            messages.error(request, "مبلغ درخواستی بیشتر از موجودی کیف پول میباشد", 'danger')
            return back_to_previous_page(request)
        
        try:
            NursePayRequest.objects.create(nurse=nurse_user.custom_user_id, amount=money_info, wallet=nurse_wallet)
            messages.success(request, "درخواست شما ثبت و در حال بررسی است", 'success')
        except Exception:
            messages.error(request, "خطا در ثبت درخواست", 'danger')
            return back_to_previous_page(request)
        
        return redirect('nurse_users:nurse_wallet')


        


        