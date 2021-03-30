import time

from django.db import models
from django.contrib.auth.models import User

from rest_framework import status as status_codes

from .field_validators import validate_pincode, validate_phone_no

from utilities.exception_utilities import InvalidUserException, InvalidContentException, CustomException


# Create your models here.


def get_user_or_raise_exception(user_id):
    try:
        return User.objects.get(pk=user_id)
    except:
        response = {
            'success': False,
            'error_message': f'User with id {user_id} does not exist :('
        }
        raise InvalidUserException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)


def get_user_or_none(user_id):
    try:
        return User.objects.get(pk=user_id)
    except:
        return None


def get_user_by_email_or_raise_exception(email):
    try:
        return User.objects.get(email=email)
    except:
        response = {
            'success': False,
            'error_message': f'User with email {email} does not exist :('
        }
        raise InvalidUserException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)


def get_user_by_email_or_none(email):
    try:
        return User.objects.get(email=email)
    except:
        return None


User.add_to_class("get_user_or_raise_exception", get_user_or_raise_exception)
User.add_to_class("get_user_or_none", get_user_or_none)
User.add_to_class("get_user_by_email_or_raise_exception", get_user_by_email_or_raise_exception)
User.add_to_class("get_user_by_email_or_none", get_user_by_email_or_none)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True)
    phone_no = models.BigIntegerField(null=False,
                                      validators=[
                                          validate_phone_no
                                      ])
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pin_code = models.BigIntegerField(null=False,
                                      validators=[
                                          validate_pincode
                                      ])

    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        current_time = time.time()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(Profile, self).save(*args, **kwargs)

    @staticmethod
    def get_profile_or_raise_exception(user_id):
        try:
            return Profile.objects.get(user_id=user_id)
        except:
            response = {
                'success': False,
                'error_message': f'User with id {user_id} does not have a profile :('
            }
            raise InvalidUserException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_profile_or_none(user_id):
        try:
            return Profile.objects.get(user_id=user_id)
        except:
            return None

    def validate_date_and_raise_exception(self):

        try:
            self.full_clean()

        except Exception as e:
            response = {
                'success': False,
                "error": e.args[0]
            }
            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)


class Category(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Content(models.Model):

    class Meta:
        ordering = ['-id']

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30, null=False)
    body = models.CharField(max_length=300, null=False)
    summary = models.CharField(max_length=60, null=False)
    pdf = models.TextField(null=False)
    categories = models.ManyToManyField(Category)

    created_at = models.BigIntegerField(default=0)
    updated_at = models.BigIntegerField(default=0)

    def save(self, *args, **kwargs):
        current_time = time.time()

        if self.created_at == 0:
            self.created_at = current_time

        self.updated_at = current_time

        super(Content, self).save(*args, **kwargs)

    @staticmethod
    def get_content_with_id_or_raise_exception(content_id):
        try:
            return Content.objects.get(pk=content_id)
        except:
            response = {
                'success': False,
                'error_message': f'Content with id {content_id} does not exist :('
            }
            raise InvalidContentException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_content_with_id_or_none(content_id):
        try:
            return Content.objects.get(pk=content_id)
        except:
            return None

    def validate_date_and_raise_exception(self):

        try:
            self.full_clean()

        except Exception as e:
            response = {
                'success': False,
                "error": e.args[0]
            }
            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)
