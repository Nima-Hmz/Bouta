# nurse_users/views/__init__.py

from . import dashboard, register, nurse_detail, service_dashboard, wallet

# Export individual modules as namespaces

__all__ = ['register', 'dashboard', 'nurse_detail', 'service_dashboard', 'wallet']