from django.urls import path
from nurse_users.views import register, dashboard, nurse_detail, service_dashboard, wallet
from .converters import UnicodeSlugConverter

app_name = 'nurse_users'

urlpatterns = [
    # register urls
    path('already-register/', register.NurseAlreadyRegisterView.as_view(), name="register"),
    path('new-register/', register.NurseNewRegisterView.as_view(), name="new_register"),
    path('register/verify/', register.NurseRegisterVertifyView.as_view(), name='register_vertify'),
    path('register/verify/set_password/', register.NurseRegisterSetPass.as_view(), name='register_setpass'),

    # nurse panel urls 
    path('dashboard/', dashboard.DashboardView.as_view(), name="dashboard"),
    path('dashboard/update-base/', dashboard.UpdateBaseView.as_view(), name="update_base"),
    path('dashboard/update-additional/', dashboard.UpdateAdditionalView.as_view(), name="update_additional"),
    path('dashboard/update-workinghour/', dashboard.UpdateWorkingHoursView.as_view(), name='update_working_hour'),
    path('dashboard/delete-workinghour/', dashboard.DeleteWorkingHours.as_view(), name="delete_working_hour"),
    path('dashboard/update-workexperience/', dashboard.UpdateWorkExperienceView.as_view(), name="update_workexperience"),
    path('dashboard/delete-workexperience/', dashboard.DeleteWorkExperience.as_view(), name="delete_workexperience"),
    path('dashboard/update-location/', dashboard.UpdateNurseLocationView.as_view(), name="update_location"),
    # path('dashboard/update-price/', dashboard.UpdateNurseSubSkillPrice.as_view(), name='update_price'),
    path('dashboard/update-description/', dashboard.UpdateDescriptionView.as_view(), name="update_description"),

    # services dashboard 
    path('dashboard/services/', service_dashboard.ServiceDashboardView.as_view(), name="service_dashboard"),
    path('dashboard/services/wallet/', wallet.NurseWalletView.as_view(), name="nurse_wallet"),
    path('dashboard/services/wallet/update-bankinfo/', wallet.NurseBankInfoInputView.as_view(), name="nurse_update_bankinfo"),
    path('dashboard/services/wallet/send-pay-request/', wallet.NursePayView.as_view(), name="nurse_pay_request"),
    path('dashboard/services/history/', service_dashboard.NurseServiceHistory.as_view(), name="service_history"),
    path('dashboard/services/<slug:service_id>/', service_dashboard.ServiceDashboardDetailView.as_view(), name="service_detail"),

    # nurse detail
    path('<uslug:slug>/', nurse_detail.NurseDetailView.as_view(), name="nurse_detail"),
    path('<uslug:nurse_slug>/service/<uslug:skill_slug>/', nurse_detail.NurseDetailSkillView.as_view(), name="nurse_detail_skill"),

]