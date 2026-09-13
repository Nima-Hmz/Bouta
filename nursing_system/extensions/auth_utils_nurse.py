from jdatetime import datetime
from django.conf import settings
from PIL import Image
from django.contrib.gis.geos import GEOSGeometry, Polygon
from nurse_users.models import EducationLevel
from django.shortcuts import render
import os
import uuid
import re

import boto3
from django.conf import settings

def jalali_convertor(jalali_date):
    jalali_datetime = datetime.strptime(jalali_date, "%Y/%m/%d").date()
    gregorian_datetime = jalali_datetime.togregorian()
    return gregorian_datetime


def is_valid_name(first_name):
    max_length = 49  # Maximum allowed length

    # Check if the name is not None
    if first_name is None:
        return False

    # Strip leading/trailing spaces
    first_name = first_name.strip()

    # Check if the name is not empty after trimming spaces
    if not first_name:
        return False

    # Check if the name length is within the valid range
    if len(first_name) < 2 or len(first_name) > max_length:
        return False

    # Check if the name contains only Persian characters and spaces
    if not re.match(r"^[\u0600-\u06FF\s]+$", first_name):
        return False

    return True


def is_valid_image(image_file):
    # Define allowed image formats
    ALLOWED_FORMATS = {"JPEG", "PNG", "JPG"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    if not image_file:
        return False

    # Check file size
    image_file.seek(0, os.SEEK_END)  # Move to the end of file
    file_size = image_file.tell()  # Get file size in bytes
    image_file.seek(0)  # Reset file pointer to start
    if file_size > MAX_FILE_SIZE:
        return False

    try:
        # Open the image and verify without fully loading it
        img = Image.open(image_file)
        img.verify()  # Quick verification to check corruption
        
        # Ensure format is valid
        if img.format not in ALLOWED_FORMATS:
            return False
        
        return True
    
    except Exception:
        return False
    

def is_valid_sex(sex):
    """Validates the sex field (M or F)."""
    
    # Check if the sex value is one of the allowed values
    if sex not in ["M", "F"]:
        return False
    
    return True


def delete_temp_file(temp_filename):
    """ Helper function to delete a single temporary file in TEMP_UPLOAD_DIR """
    if temp_filename:
        temp_file_path = os.path.join(settings.TEMP_UPLOAD_DIR, temp_filename)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)  # Delete the file
            print(f"Deleted temp file: {temp_file_path}")  # Debugging log
        else:
            print(f"File not found: {temp_file_path}")  # Debugging log for missing file


def get_unique_filename(path):
    base, ext = os.path.splitext(path)
    unique_filename = f"{base}_{uuid.uuid4().hex}{ext}"
    return unique_filename


def get_unique_filename2(filename):
    # this works with only file name and not related to the path
    ext = filename.split('.')[-1]  # Get file extension
    unique_name = f"{uuid.uuid4().hex}.{ext}"  # Generate unique filename
    return unique_name

def is_valid_address(address):
    max_length = 299

    # Ensure that the address is not None or empty
    if not address:
        return False

    # Trim leading/trailing spaces
    address = address.strip()

    # Ensure the address is not empty after trimming
    if len(address) < 5 or len(address) > max_length:
        return False

    return True


def is_valid_work_experience(start, end):
    try:
        if start < end:
            return True
    except Exception:
        return False
    
    return False


def is_valid_price(price):

    max_price = 2147483646

    # Check if price is a positive number
    if price <= 0:
        return False

    # Check if price is not higher than the maximum price
    if price > max_price:
        return False

    return True

def is_valid_province(province):
    valid_provinces = [
    "Tehran", "Isfahan", "Fars", "Khorasan Razavi", "Mazandaran", 
    "Kerman", "East Azerbaijan", "West Azerbaijan", "Kurdistan", "Golestan", 
    "Alborz", "Semnan", "Lorestan", "Yazd", "Khuzestan", "Markazi", 
    "Qazvin", "Kohgiluyeh and Boyer-Ahmad", "Hamedan", "Qom", 
    "Chaharmahal and Bakhtiari", "Gilan", "Ardabil", "Zanjan", "Bushehr", 
    "Sistan and Baluchestan", "Hormozgan", "Ilam", "South Khorasan", "North Khorasan"
    ]      
    return province in valid_provinces 


def is_location_within_iran(location_str):
    IRAN_POLYGON = Polygon((
    (44.0, 25.0),
    (64.0, 25.0),
    (64.0, 40.0),
    (44.0, 40.0),
    (44.0, 25.0),
    ), srid=4326)

    try:
        location = GEOSGeometry(location_str, srid=4326)
    except Exception:
        return False
    
    if not IRAN_POLYGON.contains(location):
        return False
    
    return True

def is_valid_description(description):
    return len(description) <= 999


def check_national_id_number(id):
    if id is None:
        return False
    
    if len(id) < 9:
        return False
    
    if len(id) > 25:
        return False
    
    if not id.isdigit():
        return False
    
    return True


# Initialize S3 Client(bucket storage)
def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )


def return_redirect_nurse(request, input_data, template_name):
    context = {
        'education_levels': EducationLevel.objects.all(),
        'input_data':input_data,
    }
    return render(request, template_name, context=context)
    