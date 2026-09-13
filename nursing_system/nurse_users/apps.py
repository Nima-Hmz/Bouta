from django.apps import AppConfig


class NurseUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nurse_users'

    def ready(self):
        import nurse_users.signals