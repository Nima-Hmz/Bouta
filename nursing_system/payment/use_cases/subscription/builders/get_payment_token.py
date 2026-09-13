from nurse_users.models import SubscriptionPayment
from django.core.exceptions import ValidationError
from payment.getaways.config import MERCHANT_CODE, TERMINAL_CODE, PRIVATE_KEY_PEM
import json
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


class GetPaymentToken:
    def __init__(self, nurse, plan):
        self.nurse = nurse
        self.plan = plan

    def execute(self):
        self.subscription_payment = self._create_subscription_payment()
        self.content_of_body = self.create_content_of_body(self.subscription_payment)
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


    def create_content_of_body(self, subscription_payment):
        body = {         
            "InvoiceNumber": subscription_payment.invoice_number,
            "InvoiceDate": f"{subscription_payment.invoice_date}",
            "TerminalCode": f"{TERMINAL_CODE}",
            "MerchantCode": f"{MERCHANT_CODE}",
            "Amount": subscription_payment.price,
            "RedirectAddress": "https://bouta.ir/payment/subscription-result/",
            "Timestamp": f"{subscription_payment.invoice_datetime}",
            "InstallmentsCount": 1,
            "MaxCreditShare": 1,
            "Mobile": f"{self.nurse.phone_number}",
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
    

    def _create_subscription_payment(self):
        try: 
            subscription_payment = SubscriptionPayment.objects.create(nurse=self.nurse, plan=self.plan, \
                                                                       price=self.plan.price)
        except Exception as e:
            raise ValidationError("خطا در ساخت نمونه پرداخت")
        
        return subscription_payment