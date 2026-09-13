# database_router.py

class MultiDBRouter:
    def db_for_read(self, model, **hints):
        """Direct read operations to the appropriate database."""
        if model._meta.app_label == 'normal_users':
            return 'default'
        elif model._meta.app_label == 'nurse_users':
            return 'default'
        elif model._meta.app_label == 'services':
            return 'services_db'
        elif model._meta.app_label == 'articles':
            return 'content_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """Direct write operations to the appropriate database."""
        if model._meta.app_label == 'normal_users':
            return 'default'
        elif model._meta.app_label == 'nurse_users':
            return 'default'
        elif model._meta.app_label == 'services':
            return 'services_db'
        elif model._meta.app_label == 'articles':
            return 'content_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relationships between models across databases."""
        db_list = ('default', 'content_db', 'services_db')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure migrations are applied to the correct database."""
        if app_label == 'normal_users':
            return db == 'default'
        elif app_label == 'nurse_users':
            return db == 'default'
        elif app_label == 'services':
            return db == 'services_db'
        elif app_label == 'articles':
            return db == 'content_db'
        return db == 'default'