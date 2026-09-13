from ..validation.subscription_validation_domain import NurseSubscriptionValidator, TransactionResultSubscriptionValidator
from payment.use_cases.subscription.builders.check_transaction_result import CheckTransactionResult
from payment.use_cases.subscription.handlers.successful_payment import SuccessfulPayment
from nurse_users.models import SubscriptionPlan
from payment.getaways.check_payment_result import send_check_result_request

class SubscriptionCheckResult:
    def __init__(self, request):
        self.request = request

    def execute(self):
        # first validate the nurse and the subscription plan and the transaction result
        self._validate_subscription_plan()
        self.the_subscription_plan = self._fetch_subscription_plan()
        self.transaction_results = self._validate_transaction_result()
        
        # then check the result of transaction with the payment terminal
        check_transaction_result = CheckTransactionResult(self.request, self.transaction_results)
        check_transaction_result.execute()
        self.result_api_and_exceptions = self._check_result_api_and_exceptions(check_transaction_result.dump_body, check_transaction_result.header)

        # then apply_successful_payment_result
        self._check_success_payment()

        return True


    def _validate_subscription_plan(self):
        self.nurse = nurse_subscription_validator = NurseSubscriptionValidator(self.request.user).validate()
        return True
    
    def _fetch_subscription_plan(self):
        subscription_plan = SubscriptionPlan.objects.first()
        if not subscription_plan:
            raise Exception("طرح اشتراک یافت نشد")
        return subscription_plan
    
    def _validate_transaction_result(self):
        transaction_result = TransactionResultSubscriptionValidator(self.request)
        transaction_result.validate_transaction_result()
        self.subscription_payment_instance = transaction_result.get_subscription_payment_instance()
        return transaction_result.get_transaction_result()
    
    def _check_result_api_and_exceptions(self, body, header):
        self.result_status, self.result_response = send_check_result_request(body, header)
    

    def _check_success_payment(self):
        if self.result_status == True:
            self._apply_successful_payment_result()
        else:
            raise Exception("مشکل در بررسی وضعیت پرداخت در درگاه پرداخت")
    
    def _apply_successful_payment_result(self):
        successful_payment_instance = SuccessfulPayment(self.subscription_payment_instance, self.transaction_results)
        successful_payment_instance.execute()
