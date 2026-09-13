from django.urls import path
from services.views import nearby_nurses, base_service, middle_service, advance_service
from nurse_users.converters import UnicodeSlugConverter

app_name = 'services'

urlpatterns = [

    # looking for nurse
    path('nearby-nurses/', nearby_nurses.NearbyNursesView.as_view(), name="nearby_nurses"),
    path('nearby-nurses/search/', nearby_nurses.NearbyNurseSearchView.as_view(), name="nearby_nurses_search"),

    # service base
    path('nurse/service/<slug:service_id>/accept/', base_service.NurseAcceptServiceView.as_view(), name='nurse_service_accept'),
    path('nurse/service/<slug:service_id>/reject/', base_service.NurseRejectServiceView.as_view(), name='nurse_service_reject'),
    path('user/service/<slug:service_id>/user-cancel/', base_service.UserCancelServiceView.as_view(), name='user_service_cancel'),
    
    # service middle
    path('nurse/service/<slug:service_id>/nurse-end-service/', middle_service.NurseEndServiceView.as_view(), name='nurse_end_service'),
    path('nurse/service/<slug:service_id>/service-cancel/', middle_service.NurseCancelServiceView.as_view(), name='nurse_middle_cancel' ),
    path('user/service/<slug:service_id>/user-end-service/', middle_service.UserEndServiceView.as_view(), name='user_end_service'),
    path('user/service/<slug:service_id>/user-middle-cancel', middle_service.UserMiddleCancelServiceView.as_view(), name='user_middel_service_cancel'),

    # service advance
    path('user/service/<slug:service_id>/user-comment/', advance_service.UserRateServiceView.as_view(), name='user_rate_service'),
    path('nurse/service/<slug:service_id>/nurse-comment/', advance_service.NurseRateServiceView.as_view(), name='nurse_rate_service'),
    path('nurse/service/<slug:service_id>/nurse-report/', advance_service.NurseReportView.as_view(), name='nurse_report_service'),
    path('user/service/<slug:service_id>/user-report/', advance_service.UserReportView.as_view(), name='user_report_service'),

    path('<uslug:nurse_slug>/service/<uslug:skill_slug>/service-create/', base_service.ServiceCreateView.as_view(), name="service_create"),

]

