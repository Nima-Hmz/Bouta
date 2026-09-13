from ..validation.service_payment_validation import ServicePaymentValidation
from payment.use_cases.service_payment.builders.get_payment_token import GetPaymentToken
from payment.getaways.get_payment_token_request import send_get_payment_token_request
from payment.getaways.config import TERMINAL_BASE_URL, TERMINAL_USER_REDIRECT_TO_PAY
from services.models import ServiceRequest

class ServicePaymentRequest:
    def __init__(self, request, service_id):
        self.request = request
        self.service_id = service_id

    def execute(self):
        # first fetch the service_request
        self._fetch_service_request()

        # second validate the user and the service_request
        service_payment_validation = ServicePaymentValidation(self.request, self.service_request)
        service_payment_validation.execute()

        # third build the get token request and send the request
        get_payment_token = GetPaymentToken(self.service_request, self.request)
        get_payment_token.execute()
        self._get_payment_token_api_and_exceptions(get_payment_token.dump_body, get_payment_token.header)

        # redirect the user to the payment terminal
        self._redirect_user_to_terminal() 
        return self.payment_terminal_url
        

    def _get_payment_token_api_and_exceptions(self, body, header):
        self.get_payment_token_status, self.get_payment_token_response = send_get_payment_token_request(self.request, \
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

    def _fetch_service_request(self):
        try:
            self.service_request = ServiceRequest.objects.get(service_request_id=self.service_id)
        except Exception:
            raise Exception("خطا در لود کردن سرویس")
        
