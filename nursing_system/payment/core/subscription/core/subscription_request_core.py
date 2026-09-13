from ..validation.subscription_validation_domain import NurseSubscriptionValidator
from nurse_users.models import SubscriptionPlan
from django.core.exceptions import ValidationError
from payment.use_cases.subscription.builders.get_payment_token import GetPaymentToken
from payment.getaways.get_payment_token_request import send_get_payment_token_request
from django.shortcuts import redirect
from payment.getaways.config import TERMINAL_BASE_URL, TERMINAL_USER_REDIRECT_TO_PAY


class SubscriptionPaymentRequestDomain:
    # the core of the nurse subscription payment request process
    def __init__(self, request):
        self.request = request

    def execute(self):
        # first validate the nurse and the subscription plan
        self._validate_subscription_plan()
        self.the_subscription_plan = self._fetch_subscription_plan()

        # then get the payment token
        get_payment_token = GetPaymentToken(self.nurse, self.the_subscription_plan)
        get_payment_token.execute()
        self._get_payment_token_api_and_exceptions(get_payment_token.dump_body, get_payment_token.header)

        # redirect the user to the payment terminal    
        self._redirect_user_to_terminal()        
        return self.payment_terminal_url
        

    def _validate_subscription_plan(self):
        self.nurse = nurse_subscription_validator = NurseSubscriptionValidator(self.request.user).validate()
        return True


    def _fetch_subscription_plan(self):
        subscription_plan = SubscriptionPlan.objects.first()
        if not subscription_plan:
            raise Exception("طرح اشتراک یافت نشد")
        return subscription_plan
    

    def _get_payment_token_api_and_exceptions(self, body, header):
        self.get_payment_token_status, self.get_payment_token_response = send_get_payment_token_request(self.request,\
                                                                                    body=body, header=header)


    def _redirect_user_to_terminal(self):
        if self.get_payment_token_status == True:
            self.payment_token = self._get_token_outof_response()
            self.payment_terminal_url = f"{TERMINAL_BASE_URL}{TERMINAL_USER_REDIRECT_TO_PAY}{self.payment_token}"
        else:
            raise Exception("مشکل در تایید احراز هویت خریدار توسط درگاه پرداخت")


    def _get_token_outof_response(self):
        data = self.get_payment_token_response.json()
        token = data.get('Token')
        if not token:
            raise Exception("جواب غیر منتظره از درگاه پرداخت")
        return token

    
    