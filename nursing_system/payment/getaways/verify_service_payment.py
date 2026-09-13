import requests
from .config import TERMINAL_BASE_URL, TERMINAL_PAYMENT_VERTIFY
from payment.use_cases.subscription.handlers.subscription_deactivator import SubscriptionDeactivator
from payment.use_cases.service_payment.handlers.unpay_service import UnpayService

def send_payment_vertify_request(body, header, service):
    # send the request to the external gateway(payment vertify)
    try:
        response = requests.post(TERMINAL_BASE_URL + TERMINAL_PAYMENT_VERTIFY, data=body, headers=header, \
                                  timeout=20)
        
        if response.status_code == 200:
            return True, response
        else:
            return False, response

    except requests.exceptions.Timeout:
        service_instance = UnpayService(service)
        service_instance.execute()
        raise Exception("مهلت اتصال به پایان رسید")
    
    except requests.exceptions.ConnectionError:
        service_instance = UnpayService(service)
        service_instance.execute()
        raise Exception("مشکل در اتصال به درگاه پرداخت")
    
    except requests.exceptions.HTTPError:
        service_instance = UnpayService(service)
        service_instance.execute()
        raise Exception("خطا در اتصال به درگاه")
    
    except Exception as e:
        service_instance = UnpayService(service)
        service_instance.execute()
        raise Exception("خطا در اتصال به درگاه")