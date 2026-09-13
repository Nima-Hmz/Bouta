from payment.getaways.config import TERMINAL_CODE, MERCHANT_CODE
import json


class CheckTransactionResult:
    def __init__(self, request, transaction_results):
        self.request = request
        self.transaction_results = transaction_results

    def execute(self):
        self.content_of_body = self.create_content_of_body()
        self.dump_body = self.dump_the_body_of_the_request(self.content_of_body)
        self.header = self.create_header_of_the_request()


    def create_header_of_the_request(self):
        header = {
            'Content-Type': 'application/json',
        } 
        return header
    
    def dump_the_body_of_the_request(self, content):
        dump_body = json.dumps(self.content_of_body, separators=(",", ":"))
        return dump_body
    

    def create_content_of_body(self):
        body = {
            "InvoiceNumber": self.transaction_results['InvoiceNumber'],
            "InvoiceDate": f"{self.transaction_results['InvoiceDate']}",
            "TerminalCode": f"{TERMINAL_CODE}",
            "MerchantCode": f"{MERCHANT_CODE}",
        }
        return body

    

