from django.views import View 
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings

class RobotsView(View):
    def get(self, request):
        # Get the hostname for building absolute URLs
        host = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        base_url = f"{protocol}://{host}"
        
        # Build absolute URLs for the sitemaps
        main_sitemap = f"{base_url}/sitemap.xml"  # Main pages only
        articles_sitemap = f"{base_url}/sitemap-articles.xml"
        categories_sitemap = f"{base_url}/sitemap-categories.xml"
        
        content = f"""User-agent: *
Disallow: /super-planet/
Disallow: /accounts/
Disallow: /tinymce/
Disallow: */login/
Disallow: */logout/
Disallow: */register/
Allow: /

# Rate limiting hint for bots
Crawl-delay: 1

# Main sitemap (contains main pages only)
Sitemap: {main_sitemap}

# Section sitemaps for content types
Sitemap: {articles_sitemap}
Sitemap: {categories_sitemap}
"""
        # Set cache control headers to improve performance
        response = HttpResponse(content, content_type="text/plain")
        response['Cache-Control'] = 'max-age=86400'  # Cache for 24 hours
        return response