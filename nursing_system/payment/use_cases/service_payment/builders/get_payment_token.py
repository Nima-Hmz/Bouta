from services.models import ServicePayment
from django.core.exceptions import ValidationError
from payment.getaways.config import MERCHANT_CODE, TERMINAL_CODE, PRIVATE_KEY_PEM
import json
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


class GetPaymentToken:
    def __init__(self, service_request, request):
        self.service_request = service_request
        self.request = request
        self.the_service_payment = service_request.payment

    def execute(self):
        self.service_payment_instance = self._create_service_payment()
        self.content_of_body = self.create_content_of_body(self.service_payment_instance)
        self.dump_body = self.dump_the_body_of_the_request(self.content_of_body)
        self.header = self.create_header_of_the_request()

    def create_header_of_the_request(self):
        the_signature = self._digital_signature()

        header = {
            'Content-Type': 'application/json',
            'Sign': the_signature
        }
        
        return header
    
    def dump_the_body_of_the_request(self, content):
        dump_body = json.dumps(self.content_of_body, separators=(",", ":"))
        return dump_body


    def create_content_of_body(self, service_payment_instance):
        body = {         
            "InvoiceNumber": service_payment_instance.invoice_number,
            "InvoiceDate": f"{service_payment_instance.invoice_date}",
            "TerminalCode": f"{TERMINAL_CODE}",
            "MerchantCode": f"{MERCHANT_CODE}",
            "Amount": service_payment_instance.price * 10,
            "RedirectAddress": "https://bouta.ir/payment/user-service-payment-result/",
            "Timestamp": f"{service_payment_instance.invoice_datetime}",
            "InstallmentsCount": 1,
            "MaxCreditShare": 1,
            "Mobile": f"{self.request.user.phone_number}",
            "CreditScore": 1,
            "ManualCreditPurchase": 1,
            "HasOtp":False
        }
        return body
        
    def _digital_signature(self):
        # Load the private key
        private_key = serialization.load_pem_private_key(
            PRIVATE_KEY_PEM,
            password=None,
        )

        # Sign the JSON-encoded data
        signature = private_key.sign(
            data=self.dump_body.encode('utf-8'),
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA1()
        )

        #  Base64-encode the signature for the HTTP header
        sign_base64 = base64.b64encode(signature).decode('utf-8')
        return sign_base64
    

    def _create_service_payment(self):
        try: 
            service_payment = ServicePayment.objects.create(payment=self.the_service_payment, \
                                                                  the_payment_id=self.the_service_payment.payment_id, \
                                                                       price=self.the_service_payment.amount)
        except Exception as e:
            raise ValidationError("خطا در ساخت نمونه پرداخت")
        
        return service_payment