from payment.getaways.config import TERMINAL_CODE, MERCHANT_CODE, PRIVATE_KEY_PEM
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import json

class VerifyTransactionPayment:
    def __init__(self, service_payment_instance):
        self.service_payment_instance = service_payment_instance

    def execute(self):
        self.content_of_body = self.create_content_of_body()
        self.dump_body = self.dump_the_body_of_the_request()
        self.header = self.create_header_of_the_request()

    def create_header_of_the_request(self):
        the_signature = self._digital_signature()

        header = {
            'Content-Type': 'application/json',
            'Sign': the_signature
        }
        
        return header
    
    def dump_the_body_of_the_request(self):
        dump_body = json.dumps(self.content_of_body, separators=(",", ":"))
        return dump_body
    
    def create_content_of_body(self):
        body = {         
            "InvoiceNumber": self.service_payment_instance.invoice_number,
            "InvoiceDate": f"{self.service_payment_instance.invoice_date}",
            "TerminalCode": f"{TERMINAL_CODE}",
            "MerchantCode": f"{MERCHANT_CODE}",
            "Timestamp": f"{self.service_payment_instance.invoice_datetime}",
            "Amount":self.service_payment_instance.price * 10,
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