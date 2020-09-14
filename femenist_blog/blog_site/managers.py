from django.db.models import Manager
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, email, date_of_birth, display_name, password = None):
        if not username:
            raise ValueError('Users must have a username')
        if not email:
            raise ValueError('Users must have a email')
        if not date_of_birth:
            raise ValueError('Users must have a date of birth')
        if not display_name:
            raise ValueError('Users must have a display name')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            date_of_birth = date_of_birth,
            password = password,
            display_name = display_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email,date_of_birth, display_name, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            date_of_birth = date_of_birth,
            password = password,
            display_name = display_name,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user