from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class IndexSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ['home:index']

    def location(self, item):
        return reverse(item)


class AboutUsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ['home:about_us']

    def location(self, item):
        return reverse(item)


class ContactUsSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ['home:contact_us']

    def location(self, item):
        return reverse(item)


class FaqSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ['home:faq']

    def location(self, item):
        return reverse(item)


class HistorySitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.6

    def items(self):
        return ['home:history']

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return ['home:service']

    def location(self, item):
        return reverse(item) 