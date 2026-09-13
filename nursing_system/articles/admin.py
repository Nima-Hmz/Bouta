from django.contrib import admin
from .models import Article, Category, BaseTemplateModel, IndexTemplateModel, ServiceTemplateModel, \
    FrequentQuestionsTemplateModel, ContactUsTemplateModel, TermsTemplateModel, HistoryTemplateModel
from django_jalali.admin.filters import JDateFieldListFilter

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'star', 'jalali_datetime')
    list_filter = (
        ('jalali_datetime', JDateFieldListFilter),
    )
    search_fields = ('title', 'slug')
admin.site.register(Article, ArticleAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'star')
    list_filter = (
        'star',
    )
    search_fields = ('title', 'slug')
admin.site.register(Category, CategoryAdmin)

admin.site.register(BaseTemplateModel)
admin.site.register(IndexTemplateModel)
admin.site.register(ServiceTemplateModel)
admin.site.register(FrequentQuestionsTemplateModel)
admin.site.register(ContactUsTemplateModel)
admin.site.register(TermsTemplateModel)
admin.site.register(HistoryTemplateModel)