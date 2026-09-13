from django.contrib.auth.models import BaseUserManager
from django.db import IntegrityError
import uuid



class UserManager(BaseUserManager):
    def create_user(self, phone_number, user_name, password, **extra_fields):
        if not phone_number:
            raise ValueError('user must have phone number')
        
        elif not user_name:
            raise ValueError('user must have full name')
        
        elif not password:
            raise ValueError('user must have password')

        while True:
            try: 
                unique_identifier = uuid.uuid4()
                user = self.model(phone_number=phone_number, user_name=user_name, user_id=unique_identifier, \
                                   **extra_fields)
                user.set_password(password)
                user.save()
                break
            except IntegrityError:
                continue

        return user
    
    def create_superuser(self , phone_number, user_name, password):

        while True: 
            try:
                user = self.create_user(phone_number=phone_number, user_name=user_name, password=password)
                user.is_admin = True
                user.save()
                break
            except IntegrityError:
                continue
    
        return user
    
