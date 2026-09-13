from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.timezone import now
from datetime import timedelta

class CustomUser(AbstractBaseUser, PermissionsMixin):
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

    user_id = models.UUIDField(unique=True, editable=False)
    phone_number = models.CharField(max_length=11, unique=True)
    user_name = models.CharField(max_length=124)
    province = models.CharField(max_length=50, choices=PROVINCE_CHOICES, default='Tehran')
    city = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=124, blank=True, null=True)
    average_rating = models.FloatField(null=True, blank=True)
    rating_count = models.PositiveIntegerField(default=0)

    is_nurse = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self) :
        return self.phone_number
    
    def has_perm(self , perm , obj=None):
        return True
    
    def has_module_perms(self , app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
    
    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class OtpCodeModel(models.Model):
    phone_number = models.CharField(max_length=11)
    otp          = models.PositiveSmallIntegerField()
    created      = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'{self.phone_number} - {self.otp} - {self.created}'
    
    def is_expired(self):
        expiration_time = timedelta(minutes=2)
        return now() > self.created + expiration_time
    
    def cleanup_expired():
        expiration_time = timedelta(minutes=3)
        OtpCodeModel.objects.filter(created__lt=now() - expiration_time).delete()
    
    class Meta:
        verbose_name_plural = 'کد های تایید'
        verbose_name = 'کد تاییدی'

