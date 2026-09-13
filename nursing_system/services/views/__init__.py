# services/views/__init__.py

from . import nearby_nurses, base_service, middle_service, advance_service

# Export individual modules as namespaces

__all__ = ['nearby_nurses', 'base_service', 'middle_service', 'advance_service']