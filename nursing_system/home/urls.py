from django.urls import path
from home.views import info, home

app_name = 'home'

urlpatterns = [

    # home
    path('', home.IndexView.as_view(), name='index'),

    path('about-us/', home.AboutUsView.as_view(), name='about_us'),
    path('contact-us/', home.ContactView.as_view(), name='contact_us'),
    path('faq/', home.FAQView.as_view(), name='faq'),
    path('history/', home.HistoryView.as_view(), name='history'),
    path('service/', home.ServiceView.as_view(), name='service'),
    path('terms/', home.TermsView.as_view(), name='terms'),

    # info
    path('service-pricing/', info.ServicePricingView.as_view(), name='service_pricing'),

]
