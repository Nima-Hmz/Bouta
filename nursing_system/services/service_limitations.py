from .models import ServiceRequest
from django.db.models import Q
from django.db import models, transaction

def user_pending_services(user_instance):
    # the count of user pending requests
    return ServiceRequest.objects.filter(user=user_instance.user_id, status='pending', closed=False).count()

def user_open_services(user_instance):
    # Returns the count of open service requests that are in 'pending' or 'payment_pending' status
    return ServiceRequest.objects.filter(
        user=user_instance.user_id,
        closed=False,
        status__in=['accepted', 'payment_pending']
    ).count()

def user_unpaid_services(user_instance):
    # the count of user unpaid requests(the ones that are still open)
    unpaid_count = ServiceRequest.objects.filter(
        user=user_instance.user_id,
        closed=False,
        status__in=['accepted', 'payment_pending']
    ).filter(
        Q(payment__isnull=True) | Q(payment__payment_status=False)
    ).count()

    return unpaid_count

def nurse_active_services(nurse_instance):
    # the count of the nurse active services
    return ServiceRequest.objects.filter(nurse=nurse_instance.custom_user_id, status='accepted', closed=False).count()


def check_user_request_service_limits(user_instance, nurse_instance):
    """the main function of checking the service limits for users when sending a service request"""

    # user limits 
    max_user_pending_service_limit = 3
    max_user_open_service_limit = 3
    max_user_unpaid_service_limit = 1

    # nurse limits 
    max_nurse_open_service_limit = 100

    # results 
    result = True # True if the service can be created
    message = "" # the message of the error

    if user_unpaid_services(user_instance) >= max_user_unpaid_service_limit:
        result = False
        message = f"کاربر دارای بیش از {max_user_unpaid_service_limit} خدمت پرداخت نشده است"
        return result, message

    if user_pending_services(user_instance) >= max_user_pending_service_limit:
        result = False
        message = f"کاربر دارای بیش از {max_user_pending_service_limit} درخواست فرستاده شده در حالت انتظار است"
        return result, message
    
    if user_open_services(user_instance) >= max_user_open_service_limit:
        result = False
        message = f"کاربر دارای بیش از {max_user_open_service_limit} خدمت فعال است"
        return result, message
    
    if nurse_active_services(nurse_instance) >= max_nurse_open_service_limit:
        result = False
        message = f"پرستار مورد نظر دارای بیش از {max_nurse_open_service_limit} میباشد"
        return result, message
    
    return result, message


def check_nurse_accept_service(service, nurse):
    """the main function of checking the service limits for nurses when accepting a service request"""

    # nurse_limits 
    max_nurse_open_service_limit = 3

    # results 
    result = True # True if the service can be created
    message = "" # the message of the error

    if service.is_expired():
        try:
            with transaction.atomic():
                service.status = 'cancelled'
                service.closed = True
                service.save(update_fields=['status', 'closed', 'updated_at'])
        except Exception:
            print('error at changing the expired status')
            
        result = False
        message = "مهلت پذیرفتن سرویس به پایان رسیده است"
        return result, message

    if service.closed:
        result = False
        message = 'درخواست بسته شده یا لغو شده است'
        return result, message

    if service.status != 'pending':
        result = False
        message = 'درخواست لغو شده یا حالت آن تغییر کرده'
        return result, message
    
    if nurse_active_services(nurse) >= max_nurse_open_service_limit:
        result = False
        message = f'شما نمیتوانید بیشتر از {max_nurse_open_service_limit} خدمت فعال داشته باشید'
        return result, message
    
    return result, message
    

def check_nurse_reject_service(service):
    """the main function of checking the service limits for nurses when rejecting a service request"""
    
    # results 
    result = True # True if the service can be created
    message = "" # the message of the error
    
    if service.closed:
        result = False
        message = 'درخواست بسته شده یا لغو شده است'
        return result, message
    
    if service.status != 'pending':
        result = False
        message = 'درخواست لغو شده یا حالت آن تغییر کرده'
        return result, message
    
    return result, message


def check_user_cancel_service(service):
    """the main function of checking the service limits for users when cancel a service request
    this when works only when the service is not accepted by the nurse
    i want to seprate this so i can prevent user to see the nurse phone number and contact detail"""
     
    # results 
    result = True # True if the service can be created
    message = "" # the message of the error
    
    if service.closed:
        result = False
        message = 'درخواست بسته شده یا لغو شده است'
        return result, message
    
    if service.status != 'pending':
        result = False
        message = 'درخواست لغو شده یا حالت آن تغییر کرده'
        return result, message
    
    return result, message



def check_nurse_cancel_service(service):
    """the main function of checking the service limits for nurses when cancelling a service request"""
    
    # results 
    result = True # True if the service can be created
    message = "" # the message of the error
    
    if service.closed:
        result = False
        message = 'درخواست بسته شده یا لغو شده است'
        return result, message
    
    if service.status != 'accepted':
        result = False
        message = 'درخواست لغو شده یا حالت آن تغییر کرده'
        return result, message
    
    if service.payment.payment_status:
        result = False
        message = 'مبلغ خدمت پرداخت شده است و توانایی لغو خدمت وجود ندارد'
        return result, message
    
    return result, message


def check_user_middle_cancel_service(service):
    """the main function of checking the service limits for users when cancel a service request
    in the middle of the service this when works only when the service is not accepted by the nurse
    i want to seprate this so i can prevent user to see the nurse phone number and contact detail"""
     
    # results 
    result = True # True if the service can be created
    message = "" # the message of the error
    
    if service.closed:
        result = False
        message = 'درخواست بسته شده یا لغو شده است'
        return result, message
    
    if service.status != 'accepted':
        result = False
        message = 'درخواست لغو شده یا حالت آن تغییر کرده'
        return result, message
    
    if service.payment.payment_status:
        result = False
        message = 'مبلغ خدمت پرداخت شده است و توانایی لغو خدمت وجود ندارد'
        return result, message
    
    return result, message

def check_nurse_end_service(service):
    # results 
    result = True # True if the service can be created
    message = "" # the message of the error
    
    if service.closed:
        result = False
        message = 'درخواست بسته شده یا لغو شده است'
        return result, message
    
    if service.status != 'accepted':
        result = False
        message = 'درخواست لغو شده یا حالت آن تغییر کرده'
        return result, message
    
    return result, message


def check_user_end_service(service):
    # results 
    result = True # True if the service can be created
    message = "" # the message of the error

    if service.closed:
        result = False
        message = 'درخواست بسته شده یا لغو شده است'
        return result, message
    
    if service.status != 'accepted':
        result = False
        message = 'درخواست لغو شده یا حالت آن تغییر کرده'
        return result, message
    
    if not service.payment.payment_status:
        result = False
        message = 'تا پرداخت مبلغ خدمت شما قادر به پایان دادن به خدمت نیستید'
        return result, message
    
    return result, message

def check_user_rate(service):
    # results 
    result = True # True if the service can be created
    message = "" # the message of the error

    if not service.closed:
        result = False
        message = 'خدمت هنوز در وضعیت های باز قرار دارد'
        return result, message
    
    if service.status != 'completed':
        result = False
        message = 'خدمت هنوز در وضعیت های باز قرار دارد'
        return result, message
    
    return result, message


def check_nurse_rate(service):
    # results
    result = True # True if the service can be created
    message = "" # the message of the error

    if not service.closed:
        result = False
        message = 'خدمت هنوز در وضعیت های باز قرار دارد'
        return result, message
    
    if service.status != 'completed':
        result = False
        message = 'خدمت هنوز در وضعیت های باز قرار دارد'
        return result, message
    
    return result, message