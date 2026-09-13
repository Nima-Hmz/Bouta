from django.core.validators import MinValueValidator, MaxValueValidator
from django_jalali.db import models as jmodels
from django.db import models, transaction, IntegrityError
from django.utils import timezone
import datetime
from django.db import models
import jdatetime
import uuid

# Create your models here.

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('accepted', 'پذیرفته شده و در حال اجرا'),
        ('payment_pending', 'در انتظار پرداخت'),
        ('completed', 'پایان یافته'),
        ('cancelled', 'لغو شده'),
        ('reject', 'رد شده'),
        ('user_cancelled', 'لغو توسط کاربر')
    ]

    service_request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    skill_slug = models.SlugField(allow_unicode=True)
    skill_title = models.CharField(max_length=124)
    user = models.UUIDField(db_index=True)
    nurse = models.UUIDField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    closed = models.BooleanField(default=False)
    service_detail_user = models.TextField(max_length=1000, null=True, blank=True)
    j_created_at = jmodels.jDateTimeField(default=jdatetime.datetime.now)
    created_at = models.DateTimeField(auto_now_add=True) 
    j_update_at = jmodels.jDateTimeField(default=jdatetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Define the expiration period in days
    EXPIRATION_DAYS = 3

    def __str__(self):
        return f"{self.service_request_id}"
    
    class Meta:
        verbose_name = "درخواست خدمات"
        verbose_name_plural = "درخواست خدمات"
        ordering = ('-j_created_at',)

    def get_total_price(self):
        return sum(item.get_cost() for item in self.service_item.all())
    
    def is_expired(self):
        """
        Check if the service request has expired.
        A request is considered expired if 3 days have passed since its creation.
        """
        expiration_time = self.created_at + datetime.timedelta(days=self.EXPIRATION_DAYS)
        return timezone.now() > expiration_time
    
    def accept_and_cancel_others(self):
        """
        Marks this service request as accepted and, in an atomic transaction,
        cancels all other pending requests of the same user by setting their
        status to 'cancelled' and closed=True.
        """
        try:
            with transaction.atomic():
                # Refresh the service request to get the latest status from the database.
                self.refresh_from_db()

                # Re-check the status to avoid race conditions.
                if self.status != 'pending':
                    return False
                
                # Accept this service request
                self.status = 'accepted'
                self.save(update_fields=['status', 'updated_at'])
                
                # Cancel all other pending requests of the same user
                ServiceRequest.objects.filter(
                    user=self.user,
                    status='pending'
                ).exclude(pk=self.pk).update(status='user_cancelled', closed=True)
        except Exception:
            return False
        
        return True
    
    def reject_service(self):
        """
        Marks the service request as rejected.
        This method assumes that all necessary validations have been done beforehand.
        """
        try:
            with transaction.atomic():
                # Refresh the service request to get the latest status from the database.
                self.refresh_from_db()

                # Re-check the status to avoid race conditions.
                if self.status != 'pending':
                    return False

                # change the mark
                self.status = 'reject'
                self.closed = True
                self.save(update_fields=['status', 'closed', 'updated_at'])
        except Exception:
            return False
        return True
    
    def user_cancel_service(self):
        """
        Marks the service request as cancel by the user.
        This method assumes that all necessary validations have been done beforehand.
        """
        try:
            with transaction.atomic():
                # Refresh the service request to get the latest status from the database.
                self.refresh_from_db()

                # Re-check the status to avoid race conditions.
                if self.status != 'pending':
                    return False

                self.status = 'user_cancelled'
                self.closed = True
                self.save(update_fields=['status', 'closed', 'updated_at'])
        except Exception:
            return False
        return True
    

    def nurse_cancel_service(self):
        try:
            with transaction.atomic():
                # Refresh the service request to get the latest status from the database.
                self.refresh_from_db()

                # Re-check the status to avoid race conditions.
                if self.status != 'accepted':
                    return False

                # change the mark
                self.status = 'cancelled'
                self.closed = True
                self.save(update_fields=['status', 'closed', 'updated_at'])
        except Exception:
            return False
        return True
    
    def user_middle_cancel_service(self):
        try:
            with transaction.atomic():
                # Refresh the service request to get the latest status from the database.
                self.refresh_from_db()

                # Re-check the status to avoid race conditions.
                if self.status != 'accepted':
                    return False

                # change the mark
                self.status = 'cancelled'
                self.closed = True
                self.save(update_fields=['status', 'closed', 'updated_at'])
        except Exception:
            return False
        return True
    
    def nurse_end_service(self):
        try:
            with transaction.atomic():
                # Refresh the service request to get the latest status from the database.
                self.refresh_from_db()

                # Re-check the status to avoid race conditions.
                if self.status != 'accepted':
                    return False
                
                if self.payment.payment_status == False:
                    # change the mark
                    self.status = 'payment_pending'
                    self.save(update_fields=['status', 'updated_at'])
                else: 
                    # change the mark
                    self.status = 'completed'
                    self.closed = True
                    self.save(update_fields=['status', 'closed', 'updated_at'])
        except Exception:
            return False
        return True
    
    def user_end_service(self):
        try:
            with transaction.atomic():
                # Refresh the service request to get the latest status from the database.
                self.refresh_from_db()

                # Re-check the status to avoid race conditions.
                if self.status != 'accepted':
                    return False
                
                if self.payment.payment_status == False:
                    return False
                else: 
                    # change the mark
                    self.status = 'completed'
                    self.closed = True
                    self.save(update_fields=['status', 'closed', 'updated_at'])
        except Exception:
            return False
        return True



class ServiceItem(models.Model):
    service = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="service_item")
    subskill = models.UUIDField()
    subskill_title = models.CharField(max_length=124)
    price = models.PositiveBigIntegerField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id}"
    
    def get_cost(self):
        return self.price*self.quantity
    
    class Meta:
        verbose_name = "خدمات داخل درخواست"
        verbose_name_plural = "خدمات داخل درخواست"
        ordering = ("-id",)


class Payment(models.Model):
    payment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='payment')
    amount = models.PositiveIntegerField()
    payment_status = models.BooleanField(default=False)
    j_payment_date = jmodels.jDateTimeField(null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True) 

    # commission
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    commission_amount = models.PositiveIntegerField()
    net_amount = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # If commission details are not set, calculate them using the current global commission
        if self.commission_percentage is None:
            commission = Commission.objects.first()
            if commission:
                self.commission_percentage = commission.percentage
                self.commission_amount = (self.amount * commission.percentage) / 100 
                self.net_amount = self.amount - self.commission_amount
            else:
                self.commission_percentage = 0 
                self.commission_amount = 0 
                self.net_amount = self.amount
        super(Payment, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_id}"
    
    class Meta:
        verbose_name = "پرداخت خدمت"
        verbose_name_plural = "پرداخت خدمت"


class Rating(models.Model):
    rating_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='rating')
    user_rating = models.FloatField(
        null=True, 
        blank=True,
        validators=[
            MinValueValidator(1),  # Minimum value of 1
            MaxValueValidator(5)   # Maximum value of 5
        ]
    )
    user_review = models.TextField(max_length=1000, blank=True, null=True)
    nurse_rating = models.FloatField(
        null=True, 
        blank=True,
        validators=[
            MinValueValidator(1),  # Minimum value of 1
            MaxValueValidator(5)   # Maximum value of 5
        ]
    )
    nurse_review = models.TextField(max_length=1000, blank=True, null=True)
    created_at = jmodels.jDateTimeField(default=jdatetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rating_id}"

    class Meta:
        verbose_name = "امتیاز دهی خدمت"
        verbose_name_plural = "امتیاز دهی خدمت"


class Commission(models.Model):
    title = models.CharField(max_length=124)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "کمیسیون سامانه"
        verbose_name_plural = "کمیسیون سامانه"  


    
class NurseWallet(models.Model):
    nurse_id = models.UUIDField(primary_key=True, editable=True)
    balance = models.PositiveBigIntegerField(default=0)
    bank_info = models.CharField(max_length=124, blank=True,null=True)
    valid_bank_info = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "کیف پول پرستار"
        verbose_name_plural = "کیف پول پرستار"

    def __str__(self):
        return f"Wallet for Nurse {self.nurse_id}"

    def credit(self, amount, reference=None):
        """
        Add funds to the wallet and log the transaction.
        :param amount: Decimal – the amount to credit.
        :param reference: Optional string reference (e.g. service_request_id)
        """
        if amount <= 0:
            raise ValueError("Credit amount must be positive.")


        with transaction.atomic():
            self.balance += amount
            self.save(update_fields=['balance', 'updated_at'])
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type=WalletTransaction.CREDIT,
                amount=amount,
                reference=reference
            )

        return True
    
    def debit(self, amount, reference=None):
        """
        Withdraw funds from the wallet and log the transaction.
        :param amount: Decimal – the amount to debit.
        :param reference: Optional string reference (e.g. withdrawal request id)
        """
        if amount <= 0:
            raise ValueError("Debit amount must be positive.")
        if self.balance < amount:
            raise ValueError("Insufficient funds in wallet.")

        with transaction.atomic():
            self.balance -= amount
            self.save(update_fields=['balance', 'updated_at'])
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type=WalletTransaction.DEBIT,
                amount=amount,
                reference=reference
            )
            
        return True

class WalletTransaction(models.Model):
    CREDIT = 'واریز'
    DEBIT = 'برداشت'
    TRANSACTION_TYPE_CHOICES = [
        (CREDIT, 'واریز'),
        (DEBIT, 'برداشت'),
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    wallet = models.ForeignKey(NurseWallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=8, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.PositiveBigIntegerField()
    reference = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    j_time = jmodels.jDateTimeField(default=jdatetime.datetime.now)

    class Meta:
        verbose_name = "تراکنش های کیف پول"
        verbose_name_plural = "تراکنش های کیف پول"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} on {self.timestamp}"
    

class BankInfoRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در حال بررسی'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
    )

    wallet = models.ForeignKey(NurseWallet, on_delete=models.CASCADE, related_name='bank_info_requests')
    bank_info = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    j_update_at = jmodels.jDateTimeField(default=jdatetime.datetime.now)

    def __str__(self):
        return f"{self.wallet.nurse_id} - {self.status}"
    
    class Meta:
        verbose_name = "درخواست بررسی اطلاعات بانکی"
        verbose_name_plural = "درخواست بررسی اطلاعات بانکی"
        ordering = ['-created_at']
    

class UserReport(models.Model):
    service_id = models.UUIDField(unique=True, editable=False)
    checked = models.BooleanField(default=False)
    description = models.TextField(max_length=1000)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ریپورت های کاربران"
        verbose_name_plural = "ریپورت های کاربران"
        ordering = ('-updated_at',)

    def __str__(self):
        return f"{self.id}"
    

class NurseReport(models.Model):
    service_id = models.UUIDField(unique=True, editable=False)
    checked = models.BooleanField(default=False)
    description = models.TextField(max_length=1000)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ریپورت های پرستاران"
        verbose_name_plural = "ریپورت های پرستاران"
        ordering = ('-updated_at',)

    def __str__(self):
        return f"{self.id}"
    

class NursePayRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در حال بررسی'),
        ('completed', 'انجام شده'),
        ('failed', 'ناموفق'),
    ]
    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nurse = models.UUIDField(db_index=True)
    wallet = models.ForeignKey(NurseWallet, on_delete=models.CASCADE, related_name='pay_request')
    amount = models.PositiveIntegerField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    j_update_at = jmodels.jDateTimeField(default=jdatetime.datetime.now)

    def __str__(self):
        return f"{self.request_id}"
    
    class Meta:
        verbose_name = "درخواست های واریز"
        verbose_name_plural = "درخواست های واریز"
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        # Determine if this is an update versus a new instance.
        is_new = self.pk is None
        previous_status = None
        if not is_new:
            previous_status = NursePayRequest.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)  # Save the instance first.

        # Process the wallet transaction only if the status is now 'completed'
        # and it has just changed to 'completed'.
        if self.status == 'completed' and (is_new or previous_status != 'completed'):
            try:
                with transaction.atomic():
                    # Call the debit method which subtracts the amount and logs the transaction.
                    if not self.wallet.debit(amount=self.amount, reference="درخواست واریز پرستار"):
                        raise Exception("Debit operation failed.")
            except Exception as e:
                # Optionally, update the status to 'failed' or handle the error appropriately.
                raise Exception(f"Error processing pay request: {e}")
                    

class ServicePayment(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="service_payment")
    the_payment_id = models.UUIDField()
    price = models.PositiveIntegerField()
    invoice_date = models.DateField(auto_now_add=True)
    invoice_datetime = models.DateTimeField(auto_now_add=True)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_paid = models.BooleanField(default=False, db_index=True)
    transaction_reference_id = models.CharField(max_length=124, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = ("تراکنش های سرویس")
        verbose_name_plural = ("تراکنش های سرویس")

        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        try:
            with transaction.atomic():
                # 1) First save to get an AutoField PK
                super().save(*args, **kwargs)

                # 2) If just created, fill in invoice_number
                if is_new:
                    dt_str = self.invoice_datetime.strftime("%Y%m%d%H%M%S")
                    # zero-pad the PK to 6 digits (adjust width as you like)
                    seq_str = f"{self.pk:06d}"
                    self.invoice_number = f"{dt_str}{seq_str}"
                    # only update the invoice_number field
                    super().save(update_fields=["invoice_number"])
        except IntegrityError as e:
            raise e

    def __str__(self):
        return f"{self.invoice_number}"