from ..builders.verify_transaction_payment import VerifyTransactionPayment
from payment.getaways.verify_service_payment import send_payment_vertify_request
from payment.use_cases.service_payment.handlers.pay_service import PayService
from payment.use_cases.service_payment.handlers.unpay_service import UnpayService



class SuccessfulPayment:
    def __init__(self, service_payment_instance, transaction_results):
        self.service_payment_instance = service_payment_instance
        self.transaction_results = transaction_results

    
    def execute(self):
        self._mark_payment_as_successful()

        pay_service_instance = PayService(self.service_payment_instance)
        pay_service_instance.execute()

        self._verify_purchase_delivery()

    def _mark_payment_as_successful(self):
        try:
            self.service_payment_instance.is_paid = True
            self.service_payment_instance.transaction_reference_id = self.transaction_results['TransactionReferenceID']
            self.service_payment_instance.save(update_fields=["is_paid", 'transaction_reference_id'])
        except Exception:
            raise Exception("خطا در تغییر وضعیت پرداخت")
        

    def _verify_purchase_delivery(self):
        # build the request and send the vertify api
        vertify_transaction_payment_instance = VerifyTransactionPayment(self.service_payment_instance)
        vertify_transaction_payment_instance.execute()
        self._vertify_payment_api_and_exceptions(vertify_transaction_payment_instance.dump_body, \
                                                 vertify_transaction_payment_instance.header)
        
        # handle the response of the vertification api
        self._handle_delivery_verification()

    def _vertify_payment_api_and_exceptions(self, body, header):
        self.vertify_api_status, self.vertify_api_response = send_payment_vertify_request(body=body, header=header, \
                                                                    service = self.service_payment_instance)
        
    def _handle_delivery_verification(self):
        if self.vertify_api_status == True:
            self._successful_verification_api()
        else:
            self._failed_verification_api()
            raise Exception("خرید شما کامل نشد. مبلغ به حساب شما بازکشت داده خواهد شد ظرف ۲۴ ساعت")
        
    def _successful_verification_api(self):
        try:
            self.service_payment_instance.is_verified = True
            self.service_payment_instance.save(update_fields=["is_verified"])
        except:
            raise Exception("خطا در ثبت تحویل اشتراک")
        
    def _failed_verification_api(self):
        subscription_deactivator_instance = UnpayService(self.service_payment_instance)
        subscription_deactivator_instance.execute()