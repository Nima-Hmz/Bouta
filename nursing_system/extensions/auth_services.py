import re
from nurse_users.models import NurseUser  
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect

# This regex is identical to the one in UnicodeSlugConverter.
ALLOWED_DISPLAY_NAME_REGEX = re.compile(
    r'^[-\w\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+$'
)

def is_valid_display_name(display_name):
    """
    Validates the display name for URL usage.
    
    This function checks that:
      1. The display name contains only valid characters for a URL,
          as defined by our custom converter's regex.
      2. The display name is unique in the database.
    
    Parameters:
      display_name (str): The user input for the display name.
    
    Returns:
      True if the display name is valid and unique.
    """
    # Check that the display name contains only allowed characters.
    if not ALLOWED_DISPLAY_NAME_REGEX.fullmatch(display_name):
        return False, 'در وارد کردن نام کاربری خود دقت کنید فاصله مجاز نمیباشد به جای آن از - یا ـ استفاده کنید'

    # Check that the display name is unique.
    if NurseUser.objects.filter(display_user_name=display_name).exists():
        return False, 'نام کاربری تکراری است'
    
    if display_name is None:
        return False, "نام کاربری را بررسی کنید"
    
    if len(display_name) < 4 or len(display_name) > 40: 
        return False, "نام کاربری را بررسی کنید"

    return True, ""


def sanitize_input(text):
    """
    Basic sanitization: trim leading and trailing whitespace.
    You could extend this function to remove unwanted HTML tags,
    but here we only strip the text.
    """
    return text.strip()

def validate_long_message(long_message):
    """
    Validates the 'long_message' input.
    """

    # Maximum allowed length for the long message
    MAX_LENGTH = 999

    # Check that the input is a string.
    if not isinstance(long_message, str):
        return False, "به توضیح وارد شده دقت کنید"
    
    # Sanitize the input.
    sanitized = sanitize_input(long_message)
    
    # Check for maximum length.
    if len(sanitized) > MAX_LENGTH:
        return False, "طول توضیح وارد شده شما زیاد است"
    
    # Check for disallowed content (e.g., <script> tags)(prevent XSS).
    if re.search(r'<script\b', sanitized, re.IGNORECASE):
        return False, "توضیح وارد شده را بررسی کنید"
    
    # If all checks pass, return the sanitized input.
    return True, sanitized


def is_validate_quantity(input_quantity):
    max_limit=100

    if input_quantity == "":
        input_quantity = 0

    try:
        quantity = int(input_quantity)
    except Exception:
        return False, "به مقدار ورودی خود دقت کنید"
    
    # Check that the quantity is not negative.
    if quantity < 0:
        return False, "تعداد نباید کمتر از صفر باشد"
    
    # Check if the quantity exceeds the maximum allowed limit.
    if quantity > max_limit:
        return False, f"تعداد ورودی غیر مجاز"
    
    # If all checks pass, return True along with the quantity.
    return True, quantity


def back_to_previous_page(request):
    current_url = request.build_absolute_uri()
    previous_url = request.META.get('HTTP_REFERER')
    
    if previous_url and url_has_allowed_host_and_scheme(
        previous_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        # Check to avoid redirect loops by ensuring the previous URL is not the same as the current URL
        if previous_url != current_url:
            return redirect(previous_url)
    
    return redirect('home:index')


def send_sms(phone_number, message):
    pass 

def map_province_zoom(request):
    # the list of provinces and their lat and lng
    PROVINCE_COORDS = {
    "Tehran": {"lat": 35.6892, "lng": 51.3890, "zoom": 10},
    "Isfahan": {"lat": 32.657,  "lng": 51.670,  "zoom": 10},
    "Fars": {"lat": 29.5918, "lng": 52.5836, "zoom": 9},
    "Khorasan Razavi": {"lat": 36.2605, "lng": 59.6168, "zoom": 9},
    "Mazandaran": {"lat": 36.5633, "lng": 53.0587, "zoom": 9},
    "Kerman": {"lat": 30.2839, "lng": 57.0834, "zoom": 9},
    "East Azerbaijan": {"lat": 38.0962, "lng": 46.2738, "zoom": 9},
    "West Azerbaijan": {"lat": 37.5523, "lng": 45.0760, "zoom": 9},
    "Kurdistan": {"lat": 35.314,  "lng": 46.998,  "zoom": 9},
    "Golestan": {"lat": 36.8411, "lng": 54.4412, "zoom": 9},
    "Alborz": {"lat": 35.8327, "lng": 50.9916, "zoom": 10},
    "Semnan": {"lat": 35.2250, "lng": 55.0083, "zoom": 10},
    "Lorestan": {"lat": 33.4878, "lng": 48.3558, "zoom": 9},
    "Yazd": {"lat": 31.8974, "lng": 54.3569, "zoom": 9},
    "Khuzestan": {"lat": 31.3203, "lng": 48.6692, "zoom": 9},
    "Markazi": {"lat": 34.0951, "lng": 49.6892, "zoom": 10},
    "Qazvin": {"lat": 36.2688, "lng": 50.0044, "zoom": 10},
    "Kohgiluyeh and Boyer-Ahmad": {"lat": 30.6684, "lng": 51.5876, "zoom": 10},
    "Hamedan": {"lat": 34.7980, "lng": 48.5146, "zoom": 10},
    "Qom": {"lat": 34.6401, "lng": 50.8764, "zoom": 10},
    "Chaharmahal and Bakhtiari": {"lat": 32.3269, "lng": 50.8661, "zoom": 10},
    "Gilan": {"lat": 37.2808, "lng": 49.5832, "zoom": 9},
    "Ardabil": {"lat": 38.2500, "lng": 48.3000, "zoom": 9},
    "Zanjan": {"lat": 36.6736, "lng": 48.4787, "zoom": 10},
    "Bushehr": {"lat": 28.9234, "lng": 50.8200, "zoom": 10},
    "Sistan and Baluchestan": {"lat": 29.4971, "lng": 60.8620, "zoom": 8},
    "Hormozgan": {"lat": 27.1833, "lng": 56.2833, "zoom": 9},
    "Ilam": {"lat": 33.6378, "lng": 46.4228, "zoom": 10},
    "South Khorasan": {"lat": 32.8663, "lng": 59.2211, "zoom": 9},
    "North Khorasan": {"lat": 37.4743, "lng": 57.3299, "zoom": 10},
    }
    
    if request.user.is_authenticated:
        user_province = request.user.province
        coords = PROVINCE_COORDS.get(user_province, PROVINCE_COORDS["Tehran"])
    else:
        coords = PROVINCE_COORDS.get("Tehran")
        
    return coords


def is_valid_description_report(long_message):
    """
    Validates the 'long_message' input.
    """

    if long_message == "":
        return False, 'پیام شما نمیتواند خالی باشد'

    # Maximum allowed length for the long message
    MAX_LENGTH = 999

    # Check that the input is a string.
    if not isinstance(long_message, str):
        return False, "به توضیح وارد شده دقت کنید"
    
    # Sanitize the input.
    sanitized = sanitize_input(long_message)
    
    # Check for maximum length.
    if len(sanitized) > MAX_LENGTH:
        return False, "طول توضیح وارد شده شما زیاد است"
    
    # Check for disallowed content (e.g., <script> tags)(prevent XSS).
    if re.search(r'<script\b', sanitized, re.IGNORECASE):
        return False, "توضیح وارد شده را بررسی کنید"
    
    # If all checks pass, return the sanitized input.
    return True, sanitized


def is_valid_bank_info(bank_info):

    if bank_info is None:
        return False

    if len(bank_info) < 10:
        return False

    if len(bank_info) > 49:
        return False
    
    return True


def is_valid_money_info(money_str):
    # Remove leading/trailing whitespace
    money_str = money_str.strip()
    
    if not money_str:
        return False
    
    try:
        amount = int(money_str)
    except ValueError:
        return False
    
    if amount < 0:
        return False
    
    # Optional: Check for an upper limit (adjust the limit as needed)
    MAX_AMOUNT = 10000000  # example maximum limit
    MIN_AMOUNT = 200000
    if amount > MAX_AMOUNT:
        return False
    
    if amount<MIN_AMOUNT:
        return False
    
    return True