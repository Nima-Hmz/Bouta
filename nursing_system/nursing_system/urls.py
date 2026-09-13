"""
URL configuration for nursing_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .robots_view import RobotsView
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import views as sitemap_views
from home.sitemaps import (
    IndexSitemap,
    AboutUsSitemap,
    ContactUsSitemap,
    FaqSitemap,
    HistorySitemap,
    ServiceSitemap
)
from articles.sitemaps import (
    ArticleListSitemap,
    ArticleSitemap,
    CategorySitemap
)

# Define separate sitemap dictionaries for each section
main_sitemaps = {
    'index': IndexSitemap,
    'about_us': AboutUsSitemap,
    'contact_us': ContactUsSitemap,
    'faq': FaqSitemap,
    'history': HistorySitemap,
    'service': ServiceSitemap,
}

article_sitemaps = {
    'article_list': ArticleListSitemap,
    'articles': ArticleSitemap,
}

category_sitemaps = {
    'categories': CategorySitemap,
}

# All sitemaps combined - used for a complete sitemap
all_sitemaps = {
    **main_sitemaps,
    **article_sitemaps,
    **category_sitemaps,
}

urlpatterns = [
    path('', include('home.urls')),
    path('accounts/', include('normal_users.urls')),
    path('nurse/', include('nurse_users.urls')),
    path('services/', include('services.urls')),
    path('articles/', include('articles.urls')),
    path('payment/', include('payment.urls')),

    path('super-planet/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),

    # Individual section sitemaps
    path('sitemap-articles.xml', sitemap, {'sitemaps': article_sitemaps}, name='sitemap-articles'),
    path('sitemap-categories.xml', sitemap, {'sitemaps': category_sitemaps}, name='sitemap-categories'),
    
    # Main sitemap.xml - now only contains the main pages
    path('sitemap.xml', sitemap, {'sitemaps': main_sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # prevent search engines from indexing admin
    path('robots.txt', RobotsView.as_view(), name="robots_file"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
