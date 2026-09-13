from django.contrib import admin
from .models import NurseUser, EducationLevel, RegistrationRequest, SubscriptionPlan, \
    Subscription, Skills, ModernNursing, AdditionalKnowledg, NurseUserAdditionalInfo, WorkingHours, \
    WorkExperience, NurseSkills, SubSkill, NurseSubSkill, SubscriptionPayment
from django_jalali.admin.filters import JDateFieldListFilter
from django.contrib.gis import admin as git_admin
from .models import NurseLocation

# Register your models here.

class NurseUserAdmin(admin.ModelAdmin):
    model = NurseUser

    list_display = ('phone_number', 'first_name', 'last_name', 'display_user_name', 'province', 'is_active')  # Show is_admin
    readonly_fields = ('custom_user_id',)
    list_filter = (
        ('birthday', JDateFieldListFilter),
        'sex', 'is_active',
    )
    search_fields = ('phone_number', 'province', 'city', 'first_name', 'last_name', 'custom_user_id')
    ordering = ('-id',)


    # to make nurse_user_id blank True at the level of the django damin
    def formfield_for_dbfield(self, db_field, **kwargs):
        # Make the specific field optional in the admin form
        if db_field.name == 'nurse_user_id':
            kwargs['required'] = False  # Make the field not required
        return super().formfield_for_dbfield(db_field, **kwargs)

admin.site.register(NurseUser, NurseUserAdmin)

admin.site.register(EducationLevel)
admin.site.register(SubscriptionPlan)

class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('nurse', 'status', 'updated_at', 'approved')
    list_filter = ('status', 'approved')
    ordering = ('-updated_at',)
admin.site.register(RegistrationRequest, RegistrationRequestAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('nurse_user', 'status', 'start_date_j', 'end_date_j', 'plan')
    list_filter = ('status',)
    ordering = ('status',)
    readonly_fields = ('start_date', 'start_date_j', 'end_date', 'end_date_j')
admin.site.register(Subscription, SubscriptionAdmin)

admin.site.register(Skills)

admin.site.register(NurseSkills)
admin.site.register(ModernNursing)
admin.site.register(AdditionalKnowledg)
admin.site.register(NurseUserAdditionalInfo)
admin.site.register(WorkingHours)
admin.site.register(WorkExperience)

class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('nurse', 'plan', 'price', 'transaction_reference_id', 'is_verified')
    readonly_fields = ('transaction_reference_id',)
    search_fields = ('transaction_reference_id',)
admin.site.register(SubscriptionPayment, SubscriptionPaymentAdmin)

admin.site.register(SubSkill)

class NurseSubSkillAdmin(admin.ModelAdmin):
    list_display = ('nurse', 'nurse_skill', 'subskill', 'custom_price')
    readonly_fields = ('nurse_subskill_uuid',)
    search_fields = ('nurse_subskill_uuid',)
admin.site.register(NurseSubSkill, NurseSubSkillAdmin)


@admin.register(NurseLocation)
class ShopAdmin(git_admin.GISModelAdmin):
    list_display = ('title', 'location')
