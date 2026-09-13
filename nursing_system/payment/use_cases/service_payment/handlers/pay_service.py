from django.db import transaction
from normal_users.models import CustomUser
from services.models import NurseWallet
from django.db import transaction
from .unpay_service import UnpayService

class PayService:
    def __init__(self, service_payment_instance):
        self.service_payment_instance = service_payment_instance
        self.payment_of_service = service_payment_instance.payment

    def execute(self):
        self._locate_the_instances()
        try:
            with transaction.atomic():
                self._service_wallet_modifier()
        except Exception as e:
            raise Exception(f"{e} خطا در خرید مبلغ تا ساعات آینده به حساب شما برگشت داده میشود")


    def _locate_the_instances(self):
        self.payment = self.service_payment_instance.payment
        self.service_request = self.service_payment_instance.payment.service_request
        self.nurse = self.service_request.nurse
        try:
            self.nurse_wallet = NurseWallet.objects.get(nurse_id=self.nurse)
            self.the_user = CustomUser.objects.get(user_id=self.service_request.user)
        except NurseWallet.DoesNotExist:
            raise Exception("خطا در لود کیف پول پرستار") 
        except CustomUser.DoesNotExist:
            raise Exception("خطا در لود کاربر")
        except Exception:
            raise Exception("خطایی در لود اتفاق افتاد")


    def _service_wallet_modifier(self):
        if self.service_request.status == "accepted":
            self._transaction_in_accepted_flag()
        
        elif self.service_request.status == "payment_pending":
            self._transaction_in_payment_pending_flag()

        else: 
            raise Exception("خطا در تغییر وضعیت سرویس")
            
            
    def _transaction_in_accepted_flag(self):
        
        with transaction.atomic():
            self.payment.payment_status = True
            self.payment.save(update_fields=["payment_status"])

            self.nurse_wallet.credit(self.payment_of_service.net_amount, 
                                        f"پرداخت کاربر {self.the_user}")
            
              
        

    def _transaction_in_payment_pending_flag(self):

        with transaction.atomic():
            self.payment.payment_status = True
            self.payment.save(update_fields=["payment_status"])

            self.service_request.status = "completed"
            self.service_request.closed = True
            self.service_request.save(update_fields=["status", "closed"])

            self.nurse_wallet.credit(self.payment_of_service.net_amount, 
                                        f"پرداخت کاربر {self.the_user}")




