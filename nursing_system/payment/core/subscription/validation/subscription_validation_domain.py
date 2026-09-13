from nurse_users.models import NurseUser, SubscriptionPayment
from django.core.exceptions import ValidationError

class NurseSubscriptionValidator:
    # the nurse validation before buying a subscription
    def __init__(self, user):
        self.user = user

    def validate(self):
        self._fetch_nurse_model()
        self._ensure_user_is_nurse()
        self._ensure_nurse_is_active()
        self._ensure_nurse_has_not_active_subscription()
        return self.nurse

    def _ensure_user_is_nurse(self):
        if not self.user.is_nurse:
            raise ValidationError("کاربر شما یک پرستار نیست")

    def _ensure_nurse_is_active(self):
        if not self.nurse.is_active:
            raise ValidationError("حساب پرستاری شما غیر فعال یا هنوز تایید نشده است")
        
    def _ensure_nurse_has_not_active_subscription(self):
        if self.nurse.has_active_subscription():
            raise ValidationError("شما قبلا اشتراک خریده اید")
        
    def _fetch_nurse_model(self):
        try:
            self.nurse = NurseUser.objects.get(custom_user_id=self.user.user_id)
        except NurseUser.DoesNotExist:
            raise ValidationError("پرستار یافت نشد")
        

class TransactionResultSubscriptionValidator:
    def __init__(self, request):
        self.request = request

    def validate_transaction_result(self):
        self._get_transaction_result()
        for field in self.results.values():
            if field is None or field.strip() == "":
                raise Exception(f"خطا در برگشت اطلاعات از درگاه پرداخت(برگشت وجه تا ۲۴ ساعت آینده)")
            
        
        try:
            self.subscription_payment_instance = SubscriptionPayment.objects.get(invoice_number=self.results['InvoiceNumber'])
        except Exception:
            raise Exception("خطا در دریافت اطلاعات از درگاه پرداخت")
            
    def get_transaction_result(self):
        return self.results
    
    def get_subscription_payment_instance(self):
        return self.subscription_payment_instance

    def _get_transaction_result(self):
        self.iN = self.request.GET.get("iN")
        self.iD = self.request.GET.get("iD")
        self.tref = self.request.GET.get("tref")
        self.results = {"InvoiceNumber":self.iN, "InvoiceDate":self.iD, "TransactionReferenceID":self.tref}



        
    
    
            