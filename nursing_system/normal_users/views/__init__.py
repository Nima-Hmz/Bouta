# normal_users/views/__init__.py

from . import register, auth, dashboard

# Export individual modules as namespaces

__all__ = ['register', 'auth', 'dashboard']