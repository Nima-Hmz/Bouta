from django.urls import path
from articles.views import base_article
from nurse_users.converters import UnicodeSlugConverter
# from .views import ArticleView

app_name = 'articles'

urlpatterns = [

    path('article-list/', base_article.ArticleListView.as_view(), name='article_list'),
    path('article-list/<uslug:article_slug>/', base_article.ArticleDetailView.as_view(), name='article_detail'),
    path('article-category/<uslug:category_slug>', base_article.ArticleCategoryView.as_view(), name='article_category'),
    path('article-search/', base_article.ArticleSearchResultView.as_view(), name='article_search')
    
]
