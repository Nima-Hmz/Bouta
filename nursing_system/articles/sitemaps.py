from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Category
from django.utils import timezone

class ArticleListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return ['articles:article_list']

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    # Set to 1000 articles per sitemap file
    # This is lower than the 50,000 limit to keep file sizes manageable
    limit = 1000 

    def items(self):
        # Get all published articles
        return Article.objects.filter(status=True)
    
    def location(self, obj):
        # Return the URL for each article
        return reverse('articles:article_detail', kwargs={'article_slug': obj.slug})
    
    def lastmod(self, obj):
        # Use the Jalali datetime if available, otherwise use current time
        # This is just an approximation since we don't have a standard lastmod field
        return timezone.now()


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        # Get all categories
        return Category.objects.all()
    
    def location(self, obj):
        # Return the URL for each category
        return reverse('articles:article_category', kwargs={'category_slug': obj.slug}) 