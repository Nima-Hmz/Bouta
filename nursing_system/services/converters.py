from django.urls.converters import register_converter
import re

class UnicodeSlugConverter:
    # Extended to cover Arabic, Persian and - _
    regex = r'[-\w\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
    

# Register the converter so it can be used in URL patterns.
register_converter(UnicodeSlugConverter, 'uslug')