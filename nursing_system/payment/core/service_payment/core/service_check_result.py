from ..validation.service_payment_validation import ServicePaymentValidation, TransactionResultServiceValidator
from payment.use_cases.service_payment.builders.check_transaction_result import CheckTransactionResult
from payment.getaways.check_payment_result import send_check_result_request
from payment.use_cases.service_payment.handlers.successful_payment import SuccessfulPayment


class ServicePaymentCheckResult:
    def __init__(self, request):
        self.request = request

    def execute(self):
        # first validate the transaction result and user and the service_request
        self.transaction_results = self._validate_transaction_result()
        service_payment_validation = ServicePaymentValidation(self.request, self.service_payment_instance.payment.service_request)
        service_payment_validation.execute()

        # second check the result of transaction with the payment terminal
        check_transaction_result = CheckTransactionResult(self.request, self.transaction_results)
        check_transaction_result.execute()
        self.result_api_and_exceptions = self._check_result_api_and_exceptions(check_transaction_result.dump_body, check_transaction_result.header)

        # then apply_successful_payment_result
        self._check_success_payment()
        return self.service_payment_instance.payment.service_request


    def _validate_transaction_result(self):
        transaction_result = TransactionResultServiceValidator(self.request)
        transaction_result.validate_transaction_result()
        self.service_payment_instance = transaction_result.get_service_payment_instance()
        return transaction_result.get_transaction_result()
    
    def _check_result_api_and_exceptions(self, body, header):
        self.result_status, self.result_response = send_check_result_request(body, header)

    def _check_success_payment(self):
        if self.result_status == True:
            self._apply_successful_payment_result()
        else:
            raise Exception("مشکل در بررسی وضعیت پرداخت در درگاه پرداخت")
        
    def _apply_successful_payment_result(self):
        successful_payment_instance = SuccessfulPayment(self.service_payment_instance, self.transaction_results)
        successful_payment_instance.execute()
