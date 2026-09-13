from django.db import models
from tinymce.models import HTMLField
from django.utils import timezone
from django_jalali.db import models as jmodels
import os
import uuid
# from extensions.utils import jalali_converter

# Create your models here.

def article_picture_path(instance, filename):
    """
    Generate a unique path for each NurseUser's profile picture, e.g.:
    storage/nurse/profile/{uuid4}.{ext}
    """
    ext = filename.split('.')[-1].lower()
    # Generate a random UUID hex string
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    # You could also include the user’s ID if you want, e.g.:
    # new_filename = f"{instance.custom_user_id.hex}_{uuid.uuid4().hex}.{ext}"
    return os.path.join('storage', 'articles', new_filename)

class Category(models.Model):
    """
    Category model that holds some sorts of categories that used in the blog
    """

    title = models.CharField(max_length=200, verbose_name=("عنوان دسته‌بندی"))
    description = models.CharField(max_length=200, verbose_name=("توضیح دسته بندی"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=("آدرس دسته‌بندی"), allow_unicode=True)
    star = models.BooleanField(default=False)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("دسته‌بندی")
        verbose_name_plural = ("دسته‌بندی ها")
        ordering = ['id']


class Article(models.Model):
    """
    Article model that holds information about articles published on the blog.
    """
    category = models.ManyToManyField(Category, verbose_name=("دسته بندی"), help_text=("دسته بندی پست خود را وارد کنید"), related_name="blog")
    title = models.CharField(max_length=200, verbose_name=("عنوان مقاله"), help_text=("عنوان مقاله را وارد کنید"))
    slug = models.SlugField(max_length=100, verbose_name=("آدرس مقاله"),unique=True, help_text=("آدرس مقاله را میتوانید از اینجا عوض کنید،(نکته: فقط در زمان ویرایش مقاله امکان تغییر آدرس وجود دارد) اما با عوض کردن آن آدرس قبلی در دسترس نخواهد بود"), allow_unicode=True)
    description = HTMLField(verbose_name=("مقاله"), help_text=("محتوای مقاله را وارد کنید"))
    description_short = models.TextField(verbose_name='توضیح کوتاه', null=True, blank=True)
    thumbnail = models.ImageField(upload_to=article_picture_path, verbose_name=("تصویر مقاله"), help_text=("تصویری که میخواهید به عنوان کاور مقاله قرار بگیرد را وارد کنید"))
    meta_thumbnail = models.CharField(max_length=124, verbose_name=("متا عکس"))
    jalali_datetime = jmodels.jDateTimeField(verbose_name=("زمان انتشار جلالی "))  # Jalali date-time field
    status = models.BooleanField(default=True, verbose_name=("وضعیت انتشار"))
    star = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = ("مقاله")
        verbose_name_plural = ("مقالات")
        ordering = ['-id']
        

class BaseTemplateModel(models.Model):
    logo = models.ImageField(upload_to='storage/home/')
    logo2 = models.ImageField(upload_to='storage/home/')
    logo3 = models.ImageField(upload_to='storage/home/')
    email = models.CharField(max_length=124)
    address = models.TextField(max_length=500)
    phone_number = models.TextField(max_length=124)
    footer_description = models.TextField(max_length=300)

    def str(self):
        return f"{self.id}"

    class Meta:
        verbose_name = ("اطلاعات پایه ای سایت")
        verbose_name_plural = ("اطلاعات پایه ای سایت")


class IndexTemplateModel(models.Model):
    first_image_url = models.URLField(null=True, blank=True)
    image1 = models.ImageField(upload_to='storage/home/')
    image1_url = models.URLField(max_length=500, null=True, blank=True)
    image2 = models.ImageField(upload_to='storage/home/')
    image2_url = models.URLField(max_length=500, null=True, blank=True)
    about1_title = models.CharField(max_length=500)
    about1_description = HTMLField()
    about2_title = models.CharField(max_length=500)
    about2_description = HTMLField()

    def str(self):
        return f"{self.id}"

    class Meta:
        verbose_name = ("اطلاعات صفحه اصلی")
        verbose_name_plural = ("اطلاعات صفحه اصلی")


class ServiceTemplateModel(models.Model):
    first_title = models.CharField(max_length=124)
    first_description = HTMLField()

    def str(self):
        return f"{self.id}"

    class Meta:
        verbose_name = ("اطلاعات صفحه خدمات")
        verbose_name_plural = ("اطلاعات صفحه خدمات")


class FrequentQuestionsTemplateModel(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    display_about = models.BooleanField(default=False)

    def str(self):
        return f"{self.id}"

    class Meta:
        verbose_name = ("اطلاعات صفحه پرسش های متداول")
        verbose_name_plural = ("اطلاعات صفحه پرسش های متداول")


class ContactUsTemplateModel(models.Model):
    email1 = models.CharField(max_length=124)
    email2 = models.CharField(max_length=124)
    phone_number1 = models.CharField(max_length=20)
    phone_number2 = models.CharField(max_length=20)
    address = models.TextField()

    def str(self):
        return f"{self.id}"

    class Meta:
        verbose_name = ("اطلاعات صفحه ارتباط با ما")
        verbose_name_plural = ("اطلاعات صفحه ارتباط با ما")


class TermsTemplateModel(models.Model):
    description = HTMLField()

    def str(self):
        return f"{self.id}"

    class Meta:
        verbose_name = ("اطلاعات صفحه شرایط و قوانین")
        verbose_name_plural = ("اطلاعات صفحه شرایط و قوانین")


class HistoryTemplateModel(models.Model):
    title1 = models.CharField(max_length=200, default="")
    title2 = models.CharField(max_length=200, default="")
    title3 = models.CharField(max_length=200, default="")
    description = HTMLField()
    description2 = HTMLField(default="")
    description3 = HTMLField(default="")

    def str(self):
        return f"{self.id}"

    class Meta:
        verbose_name = ("اطلاعات صفحه سوابق ما")
        verbose_name_plural = ("اطلاعات صفحه سوابق ما ")

