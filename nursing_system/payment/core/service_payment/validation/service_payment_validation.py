from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from services.models import ServicePayment

class ServicePaymentValidation:
    def __init__(self, request, service_request):
        self.service_request = service_request
        self.request = request

    def execute(self):
        self._user_validation()
        self._service_status_validation()
        self._service_is_closed()
        self._service_payment_status()
    
    def _user_validation(self):
        if self.request.user.user_id != self.service_request.user:
            raise PermissionDenied("خطا در احراز هویت")
        
    def _service_status_validation(self):
        valid_statuses_for_payment = ("accepted", "payment_pending")
        if self.service_request.status not in valid_statuses_for_payment:
            raise ValidationError("سرویس در وضعیت های مجاز برای پرداخت وجود ندارد")
        
    def _service_is_closed(self):
        if self.service_request.closed:
            raise ValidationError("سرویس مورد نظر بسته شده است")
        
    def _service_payment_status(self):
        if self.service_request.payment.payment_status:
            raise ValidationError("سرویس مورد نظر پرداخت شده است")
        
    

class TransactionResultServiceValidator:
    def __init__(self, request):
        self.request = request

    def validate_transaction_result(self):
        self._get_transaction_result()
        for field in self.results.values():
            if field is None or field.strip() == "":
                raise Exception(f"خطا در برگشت اطلاعات از درگاه پرداخت(برگشت وجه تا ۲۴ ساعت آینده)")
            
        
        try:
            self.service_payment_instance = ServicePayment.objects.get(invoice_number=self.results['InvoiceNumber'])
        except Exception:
            raise Exception("خطا در دریافت اطلاعات از درگاه پرداخت")
            
    def get_transaction_result(self):
        return self.results
    
    def get_service_payment_instance(self):
        return self.service_payment_instance

    def _get_transaction_result(self):
        self.iN = self.request.GET.get("iN")
        self.iD = self.request.GET.get("iD")
        self.tref = self.request.GET.get("tref")
        self.results = {"InvoiceNumber":self.iN, "InvoiceDate":self.iD, "TransactionReferenceID":self.tref}

    