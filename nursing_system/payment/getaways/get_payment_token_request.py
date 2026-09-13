import requests
import json
from .config import TERMINAL_BASE_URL, TERMINAL_GET_PEYMENT_TOKEN_URL
from payment.use_cases.subscription.builders.get_payment_token import GetPaymentToken
from django.contrib import messages
from django.shortcuts import redirect

def send_get_payment_token_request(request, body, header):
    # send the request to the external gateway(get_payment_token)
    try:
        response = requests.post(TERMINAL_BASE_URL + TERMINAL_GET_PEYMENT_TOKEN_URL, data=body, headers=header, \
                                  timeout=10)
        
        if response.status_code == 200:
            return True, response
        else:
            return False, response

    except requests.exceptions.Timeout:
        raise Exception("مهلت اتصال به پایان رسید")
    
    except requests.exceptions.ConnectionError:
        raise Exception("مشکل در اتصال به درگاه پرداخت")
    
    except requests.exceptions.HTTPError:
        raise Exception("خطا در اتصال به درگاه")
    
    except Exception as e:
        raise Exception(f"{e}")

