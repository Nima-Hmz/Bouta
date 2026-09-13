import re

def is_valid_phone_number(phone_number):
    # check if it is none
    if phone_number is None:
        return False

    # Check if the phone number is exactly 11 digits and contains only digits
    pattern = r'^[0-9]{11}$'
    if not re.match(pattern, phone_number):
        return False

    # Optional: Additional check for valid prefix (e.g., starts with '09')
    # You can add more sophisticated patterns if required
    if not phone_number.startswith('09'):
        return False

    return True


def is_valid_user_name(user_name):
    if user_name is None:
        return False
    
    # Check if the username contains only spaces
    if user_name.strip() == '':
        return False
    
    # Check length
    if len(user_name) < 4:
        return False
    
    if len(user_name) > 99:
        return False
    
    # Ensure the username contains only letters, numbers, and underscores (customizable pattern)
    if not re.match(r'^[\w]+$', user_name):
        return False
    
    return True


def is_valid_otp(input_value):
    # Check if the input is not None and is exactly 4 digits
    if input_value is not None and len(str(input_value)) == 4 and str(input_value).isdigit():
        return True
    
    return False

def is_valid_password(pass1, pass2, user_name):
    # Check for None values
    if any(value is None for value in (pass1, pass2, user_name)):
        return False
    
    # Check if passwords match
    if pass1 != pass2:
        return False
    
    # Check if password is the same as username
    if pass1 == user_name:
        return False
    
    # Check length constraints
    if len(pass1) < 6 or len(pass1) > 127:
        return False
    
    # Ensure the password is not just whitespace
    if pass1.strip() == '':
        return False

    # Validate allowed characters: English letters, digits, and specified special characters.
    # This regex only permits ASCII characters.
    allowed_pattern = r'^[A-Za-z0-9!@#$%^&*()_+={}\[\]:;"\'<>,.?/-]+$'
    if not re.match(allowed_pattern, pass1):
        return False

    return True


def is_valid_password_login(password):
    if password is None:
        return False
    
    if len(password) > 127:
        return False
    
    return True


def is_valid_password_reset(password1, password2):
    if any(value is None for value in (password1, password2)):
        return False
    
    if not password1 == password2:
        return False
    
    # Check if password contains only valid characters (letters, digits, and special characters)
    if not re.match(r'^[\w!@#$%^&*()_+={}\[\]:;"\'<>,.?/-]+$', password1):
        return False
    
    # Ensure password is not just whitespace
    if password1.strip() == '':
        return False
    
    if len(password1) < 6:
        return False
    
    if len(password1) > 127:
        return False
    
    return True
    

def send_otp_code(phone_number, code):
    pass
