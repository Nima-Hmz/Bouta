from django.urls import path
from normal_users.views import register, auth, dashboard

app_name = 'normal_users'

urlpatterns = [

    # login and register
    path('register/', register.UserRegisterView.as_view(), name='register'),
    path('register/verify/', register.UserRegisterVertifyView.as_view(), name='register_vertify'),
    path('register/verify/set-password/', register.UserRegisterSetPass.as_view(), name='register_setpass'),
    path('login/', auth.LoginView.as_view(), name='login'),
    path('logout/', auth.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/verify/', auth.PasswordResetVertifyView.as_view(), name='password_reset_vertify'),
    path('password-reset/verify/set-password/', auth.PasswordResetVertifySetView.as_view(), name='password_reset_vertify_set'),

    # dashboard
    path('dashboard/', dashboard.DashboardView.as_view(), name="user_dashboard"),
    path('dashboard/update-base/', dashboard.UpdateBaseView.as_view(), name="update_base"),
    path('dashboard/services/history/', dashboard.UserServiceHistory.as_view(), name='service_history'),
    path('dashboard/services/<slug:service_id>/', dashboard.ServiceDashboardDetailView.as_view(), name="service_detail"),

]
