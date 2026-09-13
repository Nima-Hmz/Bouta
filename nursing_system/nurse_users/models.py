from django_jalali.db import models as jmodels
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.indexes import GistIndex
from django.utils.timezone import now
from datetime import timedelta
from tinymce.models import HTMLField
from django.db.models import Index as DIndex
from django.db import transaction, IntegrityError
import uuid
import os

# Create your models here.

def nurse_profile_picture_path(instance, filename):
    """
    Generate a unique path for each NurseUser's profile picture, e.g.:
    storage/nurse/profile/{uuid4}.{ext}
    """
    ext = filename.split('.')[-1].lower()
    # Generate a random UUID hex string
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    # You could also include the user’s ID if you want, e.g.:
    # new_filename = f"{instance.custom_user_id.hex}_{uuid.uuid4().hex}.{ext}"
    return os.path.join('storage', 'nurse', 'profile', new_filename)

def identity_card_picture_path(instance, filename):
    """
    Generate a unique path for each NurseUser's profile picture, e.g.:
    storage/nurse/profile/{uuid4}.{ext}
    """
    ext = filename.split('.')[-1].lower()
    # Generate a random UUID hex string
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    # You could also include the user’s ID if you want, e.g.:
    # new_filename = f"{instance.custom_user_id.hex}_{uuid.uuid4().hex}.{ext}"
    return os.path.join('storage', 'nurse', 'identity_card', new_filename)

def ministry_proof_picture_path(instance, filename):
    """
    Generate a unique path for each NurseUser's profile picture, e.g.:
    storage/nurse/profile/{uuid4}.{ext}
    """
    ext = filename.split('.')[-1].lower()
    # Generate a random UUID hex string
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    # You could also include the user’s ID if you want, e.g.:
    # new_filename = f"{instance.custom_user_id.hex}_{uuid.uuid4().hex}.{ext}"
    return os.path.join('storage', 'nurse', 'ministry_proof', new_filename)


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=124, unique=True)
    product_uid = models.UUIDField(default=uuid.uuid4, unique=True)
    price = models.PositiveIntegerField()
    duration_days = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['price']
        verbose_name = ("طرح اشتراک")
        verbose_name_plural = ("طرح های اشتراک")

    def __str__(self):
        return f"{self.name} - ${self.price} for {self.duration_days} days"


class EducationLevel(models.Model):
    title = models.CharField(max_length=124)
    description = models.TextField()

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "مدرک تحصیلی"
        verbose_name_plural = "مدرک تحصیلی"


class NurseUser(models.Model):
        
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    PROVINCE_CHOICES = [
    ("Tehran", "تهران"),
    ("Isfahan", "اصفهان"),
    ("Fars", "فارس"),
    ("Khorasan Razavi", "خراسان رضوی"),
    ("Mazandaran", "مازندران"),
    ("Kerman", "کرمان"),
    ("East Azerbaijan", "آذربایجان شرقی"),
    ("West Azerbaijan", "آذربایجان غربی"),
    ("Kurdistan", "کردستان"),
    ("Golestan", "گلستان"),
    ("Alborz", "البرز"),
    ("Semnan", "سمنان"),
    ("Lorestan", "لرستان"),
    ("Yazd", "یزد"),
    ("Khuzestan", "خوزستان"),
    ("Markazi", "مرکزی"),
    ("Qazvin", "قزوین"),
    ("Kohgiluyeh and Boyer-Ahmad", "کهگیلویه و بویراحمد"),
    ("Hamedan", "همدان"),
    ("Qom", "قم"),
    ("Chaharmahal and Bakhtiari", "چهارمحال و بختیاری"),
    ("Gilan", "گیلان"),
    ("Ardabil", "اردبیل"),
    ("Zanjan", "زنجان"),
    ("Bushehr", "بوشهر"),
    ("Sistan and Baluchestan", "سیستان و بلوچستان"),
    ("Hormozgan", "هرمزگان"),
    ("Ilam", "ایلام"),
    ("South Khorasan", "خراسان جنوبی"),
    ("North Khorasan", "خراسان شمالی"),
]

    objects = jmodels.jManager()
        
    custom_user_id = models.UUIDField(unique=True, editable=False)
    first_name = models.CharField(max_length=99)
    last_name = models.CharField(max_length=99)
    display_user_name = models.CharField(max_length=123, unique=True)
    birthday = jmodels.jDateField(verbose_name=("تاریخ تولد"))  # Jalali date-time field
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    province = models.CharField(max_length=50, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to=nurse_profile_picture_path)
    education_level = models.ForeignKey(EducationLevel, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=11, unique=True)
    ministry_proof_picture = models.ImageField(upload_to=ministry_proof_picture_path)
    identity_card_picture = models.ImageField(upload_to=identity_card_picture_path)
    national_id_number = models.CharField(max_length=50)
    address = models.TextField(max_length=300)
    is_active = models.BooleanField(default=False)
    is_legal_entity = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.phone_number}"
    
    class Meta:
        verbose_name = "پرستار"
        verbose_name_plural = "پرستاران"

    def has_active_subscription(self):
        """Returns True if the user has an active subscription based on both status and expiration date."""
        if not hasattr(self, 'subscription'):
            return False
        sub = self.subscription
        return sub.status and sub.end_date > now().date()


class Skills(models.Model):
    title = models.CharField(max_length=124)
    slug = models.SlugField(unique=True, allow_unicode=True)
    skill_description = models.TextField(max_length=300)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "مهارت"
        verbose_name_plural = "مهارت ها"
        ordering = ('id',)


class SubSkill(models.Model):
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, related_name="sub_skill")
    title = models.CharField(max_length=124)
    subskill_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    standard_price = models.PositiveIntegerField()
    price_description = models.TextField()
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "زیر مهارت ها"
        verbose_name_plural = "زیر مهارت ها"

    def save(self, *args, **kwargs):
        """Update all related NurseSkills prices if the skill price changes, but only for lower prices."""
        old_price = None

        if self.pk:  # Check if the skill already exists in DB
            old_price = SubSkill.objects.filter(pk=self.pk).values_list("standard_price", flat=True).first()

        super().save(*args, **kwargs)  # Save the new price

        # If the price was changed, update only NurseSkills with a custom price lower than the new price
        if old_price is not None and old_price != self.standard_price:
            NurseSubSkill.objects.filter(subskill=self, custom_price__lt=self.standard_price).update(custom_price=self.standard_price)


class ModernNursing(models.Model):
    title = models.CharField(max_length=124)
    description = models.TextField()

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "آشنایی با ابزار های پرستاری مدرن"
        verbose_name_plural = "آشنایی با ابزار های پرستاری مدرن"


class AdditionalKnowledg(models.Model):
    title = models.CharField(max_length=124)
    description = models.TextField()

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "دانش اضافی"
        verbose_name_plural = "دانش های اضافی"

class NurseLocation(gis_models.Model):
    title = gis_models.CharField(max_length=124, blank=True, null=True)
    location = gis_models.PointField(srid=4326)
    address = gis_models.TextField(max_length=250, blank=True, null=True)
    province = gis_models.CharField(max_length=124, blank=True, null=True)

    class Meta:
        indexes = [GistIndex(fields=["location"])]
        verbose_name = "آدرس پرستار"
        verbose_name_plural = "آدرس پرستاران"
    

class NurseUserAdditionalInfo(models.Model):
    nurse = models.OneToOneField(NurseUser, on_delete=models.CASCADE, related_name='nurse_user_additional_info')
    modern_nursing = models.ForeignKey(ModernNursing, on_delete=models.SET_NULL, related_name='nurse_user_additional_info', null=True, blank=True)
    additional_knowledg = models.ManyToManyField(AdditionalKnowledg, related_name='nurse_user_additional_info', blank=True)
    nurse_location = models.OneToOneField(NurseLocation, on_delete=models.SET_NULL, related_name="nurse_user_additional_info", null=True, blank=True)
    part_time = models.BooleanField(default=False)
    description = models.TextField(max_length=1000, default="")
    average_rating = models.FloatField(null=True, blank=True)
    rating_count = models.PositiveIntegerField(default=0)
    star = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nurse}"
    
    class Meta:
        indexes = [
            DIndex(fields=["nurse_location"]),  # Speeds up joins with location-based queries
        ]
        verbose_name = "اطلاعات اضافی پرستاران"
        verbose_name_plural = "اطلاعات اضافی پرستاران"


class WorkExperience(models.Model):
    objects = jmodels.jManager()

    nurse_additional_info = models.ForeignKey(NurseUserAdditionalInfo, on_delete=models.CASCADE, related_name='work_experience')
    title = models.CharField(max_length=124)
    description = models.TextField(max_length=500, default="")
    start_work = jmodels.jDateField(verbose_name=("تاریخ شروع به کار"))  # Jalali date-time field
    end_work = jmodels.jDateField(verbose_name=("تاریخ پایان کار"))  # Jalali date-time field

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "مراکزی که پرستار در آن کار کرده"
        verbose_name_plural = "مراکزی که پرستار در آن کار کرده"


class WorkingHours(models.Model):
    DAYS_OF_WEEK = [
        ('zero', 'شنبه'),
        ('one', 'یکشنبه'),
        ('two', 'دوشنبه'),
        ('three', 'سه‌شنبه'),
        ('four', 'چهارشنبه'),
        ('five', 'پنج‌شنبه'),
        ('six', 'جمعه'),
        ('all', 'شنبه تا چهارشنبه')
    ]

    nurse_additional = models.ForeignKey(NurseUserAdditionalInfo, on_delete=models.CASCADE, related_name='working_hours')
    day = models.CharField(max_length=6, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time}, {self.end_time}"
    
    class Meta:
        verbose_name = "ساعت کاری"
        verbose_name_plural = "ساعات کاری"

class NurseSkills(models.Model):
    nurse = models.ForeignKey(NurseUserAdditionalInfo, on_delete=models.CASCADE, related_name="nurse_skills")
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, related_name='nurse_skill')

    class Meta:
        unique_together = ('nurse', 'skill')  # Prevents duplicate entries
        indexes = [
            DIndex(fields=["nurse", "skill"]),  # Composite index for faster filtering
        ]
        verbose_name = "مهارت های انتخاب شده پرستار"
        verbose_name_plural = "مهارت های انتخاب شده پرستار"

    def __str__(self):
        return f"{self.nurse.nurse.last_name} - {self.skill.title}"
    

class NurseSubSkill(models.Model):
    nurse = models.ForeignKey(NurseUserAdditionalInfo, on_delete=models.CASCADE, related_name="nurse_subskill")
    nurse_subskill_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    subskill = models.ForeignKey(SubSkill, on_delete=models.CASCADE, related_name="nurse_subskill")
    nurse_skill = models.ForeignKey(NurseSkills, on_delete=models.CASCADE, related_name="nurse_subskill")
    custom_price = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('nurse', 'subskill')  # Prevents duplicate entries
        indexes = [
            DIndex(fields=["nurse", "subskill"]),  # Composite index for faster filtering
        ]
        verbose_name = "زیر مهارت های انتخاب شده پرستار"
        verbose_name_plural = "زیر مهارت های انتخاب شده پرستار"

    def __str__(self):
        return f"{self.nurse} - {self.subskill}"

    def save(self, *args, **kwargs):
        """Set the default price if no custom price is provided."""
        if not self.custom_price:
            self.custom_price = self.subskill.standard_price
        super().save(*args, **kwargs)


class RegistrationRequest(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'در حال بررسی'),
        ('accepted', 'تأیید شده'),
        ('pending', 'در انتظار تصحیح توسط کاربر'),
    ]
    nurse = models.OneToOneField(NurseUser, on_delete=models.CASCADE, related_name='register_request')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    admin_message = models.CharField(max_length=124, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.updated_at}"
    
    def is_expired(self):
        expiration_time = timedelta(days=20)
        return now() > self.created + expiration_time
    
    def cleanup_expired():
        expiration_time = timedelta(days=20)
        RegistrationRequest.objects.filter(created__lt=now() - expiration_time).delete()

    class Meta:
        verbose_name = "درخواست عضویت پرستار"
        verbose_name_plural = "درخواست های عضویت پرستار"


class Subscription(models.Model):
    objects = jmodels.jManager()

    nurse_user = models.OneToOneField(NurseUser, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscription_plan')
    start_date = models.DateField(blank=True)
    start_date_j = jmodels.jDateField(blank=True)  
    end_date = models.DateField(blank=True)
    end_date_j = jmodels.jDateField(blank=True)
    status = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'end_date']),
        ]
        verbose_name = ("اشتراک")
        verbose_name_plural = ("اشتراک ها")

    def save(self, *args, **kwargs):
            """Ensure end_date is always calculated and status is updated automatically."""

            if not self.start_date:
                self.start_date = now().date()

            if self.plan:
                # Gregorian end date:
                self.end_date = self.start_date + timedelta(days=self.plan.duration_days)

                # jalali start and end date
                self.start_date_j = self.start_date # this will be converted automaticly
                self.end_date_j = self.end_date     # this will be converted automaticly

            super().save(*args, **kwargs)

    def is_active(self):
        """Returns True if the subscription is currently active."""
        return self.status == True and self.end_date > now().date()
    
    def days_left(self):
        """Returns the number of days left until the subscription expires."""
        if self.end_date and self.end_date > now().date():
            return (self.end_date - now().date()).days
        return 0  # Expired
    
    def __str__(self):
        return f"{self.nurse_user.last_name} - ({self.status})"


class SubscriptionPayment(models.Model):
    nurse = models.ForeignKey(NurseUser, on_delete=models.CASCADE, related_name='subscription_payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscription_payments')
    price = models.PositiveIntegerField()
    invoice_date = models.DateField(auto_now_add=True)
    invoice_datetime = models.DateTimeField(auto_now_add=True)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_paid = models.BooleanField(default=False, db_index=True)
    transaction_reference_id = models.CharField(max_length=124, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = ("خرید اشتراک")
        verbose_name_plural = ("خرید اشتراک ها")

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
        return f"{self.invoice_number} — {self.nurse}"
        
