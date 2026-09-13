from django.contrib import admin
from .models import ServiceRequest, Payment, Rating, ServiceItem, Commission, WalletTransaction, \
    NurseWallet, UserReport, NurseReport, BankInfoRequest, NursePayRequest, ServicePayment

# Register your models here.

admin.AdminSite.register

class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('service_request_id', 'status', 'closed', 'j_created_at')
    search_fields = ("service_request_id", "nurse", "user", "j_created_at")
    list_filter = ("status",)
    ordering = ('-j_created_at',)
    readonly_fields = ('service_request_id', 'user', 'nurse')
admin.site.register(ServiceRequest, ServiceRequestAdmin)

class ServiceItemAdmin(admin.ModelAdmin):
    search_fields = ("service__service_request_id",)
    readonly_fields = ('subskill',)
admin.site.register(ServiceItem, ServiceItemAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'payment_status', 'j_payment_date')
    search_fields = ("payment_id", "j_payment_date", "service_request__service_request_id")
    list_filter = ("payment_status",)
    ordering = ('-j_payment_date',)
    readonly_fields = ('payment_id',)
admin.site.register(Payment, PaymentAdmin)

class RatingAdmin(admin.ModelAdmin):
    search_fields = ("service_request__service_request_id",)
admin.site.register(Rating, RatingAdmin)

admin.site.register(Commission)

class NurseWalletAdmin(admin.ModelAdmin):
    list_display = ['nurse_id', 'balance', 'created_at', 'updated_at']
    search_fields = ("nurse_id",)
admin.site.register(NurseWallet, NurseWalletAdmin)

class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'wallet', 'transaction_type', 'amount', 'timestamp']
    search_fields = ("transaction_id",)
    list_filter = ("transaction_type",)
admin.site.register(WalletTransaction, WalletTransactionAdmin)


class UserReportAdmin(admin.ModelAdmin):
    list_display = ('service_id', 'updated_at', 'checked')
    search_fields = ('service_id',)
    readonly_fields = ('service_id',)
    list_filter = ('checked',)
admin.site.register(UserReport, UserReportAdmin)

class NurseReportAdmin(admin.ModelAdmin):
    list_display = ('service_id', 'updated_at', 'checked')
    search_fields = ('service_id',)
    readonly_fields = ('service_id',)
    list_filter = ('checked',)
admin.site.register(NurseReport, NurseReportAdmin)


class BankInfoRequestAdmin(admin.ModelAdmin):
    list_display = ('status', 'bank_info', 'j_update_at')
    search_fields = ('bank_info',)
    list_filter = ('status',)
admin.site.register(BankInfoRequest, BankInfoRequestAdmin)


class NursePayRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'nurse', 'amount', 'j_update_at', 'status')
    search_fields = ('request_id', 'nurse')
    readonly_fields = ('nurse',)
    list_filter = ('status',)
admin.site.register(NursePayRequest, NursePayRequestAdmin)


admin.site.register(ServicePayment)