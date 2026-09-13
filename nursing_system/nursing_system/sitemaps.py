from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticSitemap(Sitemap):
    """Sitemap for static sitemap files"""
    changefreq = "daily"
    priority = 0.9
    
    def __init__(self, name, location):
        self.name = name
        self.location_path = location
        
    def items(self):
        return [self.name]
        
    def location(self, item):
        # Return the direct path rather than attempting to reverse a URL
        return self.location_path 