from django.test import TestCase
from django.core.exceptions import ValidationError

# Create your tests here.
from django.contrib.auth.models import User
from .models import Profile, Content
from .field_validators import validate_password


class UserProfileCreateTest(TestCase):
    """ Test module for Profile model """

    first_name = "mahesh"
    last_name = "xyz"
    email = "mahesh@gmail.com"
    username = f"{first_name}_{last_name}_{email}"
    password = "Mahesh@123"

    address = ''
    city = ''
    state = ''
    country = ''

    phone_no = 1234567890
    pin_code = 543216

    def setUp(self):
        # create user
        user = User.objects.create(username=self.username,
                                   email=self.email,
                                   first_name=self.first_name,
                                   last_name=self.last_name)

        self.assertTrue(validate_password(self.password))
        # set password
        user.set_password(self.password)
        user.save()

        # create profile
        profile = Profile(user=user,
                          phone_no=self.phone_no,
                          address=self.address,
                          city=self.city,
                          state=self.state,
                          country=self.country,
                          pin_code=self.pin_code
                          )
        profile.save()

    def test_user_profile_validation(self):
        # get user
        user = User.objects.get(email=self.email)

        # check if user full name matches our own representation
        self.assertEqual(
            user.get_full_name(),
            f"{self.first_name} {self.last_name}"
        )

        profile = user.profile

        with self.assertRaises(ValidationError):
            # phone number must be of length 10 and pin-code must be of length 6
            profile.phone_no = self.phone_no * 10
            profile.pin_code = self.pin_code * 10

            profile.full_clean()

            profile.save()


class UserContentCreateTest(TestCase):
    """ Test module for Content model """

    email = "mahesh@gmail.com"
    username = "maheshroyal"

    title = ''
    body = ''
    summary = ''
    pdf = ''

    categories = ['category1']

    def setUp(self):
        # create a user with some username and email
        User.objects.create(username=self.username, email=self.email)

    def test_content_validation(self):
        # get user
        user = User.objects.get(email=self.email)

        # create content
        content = Content(user=user,
                          title=self.title,
                          body=self.body,
                          summary=self.summary,
                          pdf=self.pdf)

        content.save()

        with self.assertRaises(ValidationError):
            # title should be 30 characters only
            content.title = self.title * 500
            content.full_clean()

            content.save()

        with self.assertRaises(ValidationError):
            # body should be 300 characters only
            content.body = self.body * 400
            content.full_clean()

            content.save()

        with self.assertRaises(ValidationError):
            # summary should be 60 characters only
            content.summary = self.summary * 100
            content.full_clean()

            content.save()

        with self.assertRaises(ValidationError):
            # pdf should not be none
            content.pdf = None
            content.full_clean()

            content.save()
