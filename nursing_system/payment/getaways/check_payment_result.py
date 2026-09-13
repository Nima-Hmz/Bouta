import requests
from .config import TERMINAL_BASE_URL, TERMINAL_CHECK_RESULT

def send_check_result_request(body, header):
    # send the request to the external gateway(check result)
    try:
        response = requests.post(TERMINAL_BASE_URL + TERMINAL_CHECK_RESULT, data=body, headers=header, \
                                  timeout=20)
        
        print(response.json())
        
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
        raise Exception("خطا در اتصال به درگاه")