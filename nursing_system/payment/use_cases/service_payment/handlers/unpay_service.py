from django.db import transaction
from normal_users.models import CustomUser
from services.models import NurseWallet

class UnpayService:
    def __init__(self, service_payment_instance):
        self.service_payment_instance = service_payment_instance
        self.payment_of_service = service_payment_instance.payment

    def execute(self):
        self._locate_the_instances()
        try:
            with transaction.atomic():
                self._service_wallet_modifier()
        except:
            raise Exception("خطا در خرید مبلغ تا ساعات آینده به حساب شما برگشت داده میشود")


    def _locate_the_instances(self):
        self.payment = self.service_payment_instance.payment
        self.service_request = self.service_payment_instance.payment.service_request
        self.nurse = self.service_request.nurse
        self.service_previous_status = self.service_request.status 
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
        self._unpay_action()
            

    def _unpay_action(self):

        with transaction.atomic():
            self.payment.payment_status = False
            self.payment.save(update_fields=["payment_status"])

            self.nurse_wallet.debit(self.payment_of_service.net_amount, 
                                        f"پاک شدن خطای تراکنش کاربر  {self.the_user}")
            
            self.service_request.status = self.service_previous_status
            self.service_request.closed = False
            self.service_request.save(update_fields=["status", "closed"])

        