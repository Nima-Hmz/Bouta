
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OtpCodeModel
from django.db import IntegrityError
import uuid

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {'fields': ('phone_number', 'password', 'user_id')}),
        ('Personal Info', {'fields': ('user_name', 'province', 'average_rating', 'rating_count')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_nurse', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number','user_name', 'password1', 'password2'),
        }),
    )
    list_display = ('phone_number', 'user_name', 'is_nurse')  # Show is_admin
    readonly_fields = ('user_id',)
    list_filter = ('is_admin', 'is_active')  # Use is_admin for filtering
    search_fields = ('phone_number', 'user_name', 'user_id')
    ordering = ('-id',)

    def save_model(self, request, obj, form, change):
        # If the object is being created (not updated), set the user_id
        while True: 
            try:
                if not obj.user_id:
                    obj.user_id = uuid.uuid4()
                super().save_model(request, obj, form, change)
                break
            except IntegrityError:
                continue

admin.site.register(CustomUser, CustomUserAdmin)

class OtpCodeAdmin(admin.ModelAdmin):
    model = OtpCodeModel

    list_display = ('phone_number', 'otp', 'created')  # Show is_admin
    readonly_fields = ('otp',)
    search_fields = ('phone_number',)
    ordering = ('-created',)

admin.site.register(OtpCodeModel, OtpCodeAdmin)