import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status as status_codes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Profile, Content, Category
from .mixins import TransactionMixin
from .serializers import UserProfileSerializer, ContentSerializer
from .field_validators import validate_email, validate_password

from utilities.request_utilities import RequestUtilities
from utilities.exception_utilities import CustomException
from utilities.pagination_utilities import PaginationUtilities


# Create your views here.


class LoginOrRegisterUserView(TransactionMixin, APIView):

    def post(self, request, *args, **kwargs):

        post_data = RequestUtilities.get_post_data(request)

        # post data is expected,
        # if not received, raise exception
        if post_data is None:
            response = ViewHelper.get_error_context(False, 'Invalid params')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

        first_name = post_data.get('first_name', '')
        last_name = post_data.get('last_name', '')
        email = post_data.get('email', None)
        password = post_data.get('password', None)

        # if email is present in data, validate email
        if email is None or \
                not validate_email(email):
            response = ViewHelper.get_error_context(False, 'Invalid email')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

        # if password is present in data, validate password
        if password is not None and \
                not validate_password(password):
            response = ViewHelper.get_error_context(False, 'Invalid password')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

        user = User.get_user_by_email_or_none(email=email)

        if user is None:
            # giving unique username for user by adding email to the username,
            # if email already exists, then user will directly login
            user_name = f"{first_name}_{last_name}_{email}"
            user = User.objects.create(username=user_name,
                                       email=email,
                                       first_name=first_name,
                                       last_name=last_name
                                       )
            # user is created
            # setting the raw password to user
            user.set_password(password)
            user.save()

            # validate the received data for creating profile
            self.validate_registration_data(post_data)

            # creating user progile
            profile = self.create_profile(post_data, user)

            # serializing profile
            serialized_profile = UserProfileSerializer(profile, many=False).data

        else:
            # serializing profile
            serialized_profile = UserProfileSerializer(user.profile, many=False).data

        # get user token for authentication purpose
        token = ViewHelper.get_user_token(user)

        response = {
            'success': True,
            'token': token,
            'profile': serialized_profile
        }

        return Response(response)

    def validate_registration_data(self, data: dict):
        """
        check for missing parameters which is required to create a user and profile
        if any is missing , raises an exception
        """

        error_message = 'Required param {} missing in params'

        first_name = data.get('first_name', None)
        last_name = data.get('last_name', None)
        email = data.get('email', None)
        password = data.get('password', None)
        phone_no = data.get('phone_no', None)
        pin_code = data.get('pin_code', None)

        if first_name is None:
            missing_param = 'first_name'

        elif last_name is None:
            missing_param = 'last_name'

        elif email is None:
            missing_param = 'email'

        elif password is None:
            missing_param = 'password'

        elif phone_no is None:
            missing_param = 'phone_no'

        elif pin_code is None:
            missing_param = 'pin_code'

        else:
            return

        response = ViewHelper.get_error_context(False, error_message.format(missing_param))

        raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

    def create_profile(self, data: dict, user: User) -> Profile:
        """
        create profile for user and return profile
        """

        address = data.get('address', '')
        phone_no = data.get('phone_no', 0)
        city = data.get('city', '')
        state = data.get('state', '')
        country = data.get('country', '')
        pin_code = data.get('pin_code', 0)

        # create profile instance
        profile = Profile(user=user,
                          address=address, phone_no=phone_no,
                          city=city, state=state, country=country,
                          pin_code=pin_code)

        # validate profile data
        profile.validate_date_and_raise_exception()
        # saving profile
        profile.save()

        return profile


class UserContentView(TransactionMixin, APIView):
    """ inheriting API view class for using class based views in django """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        query_params = request.query_params

        user_id = query_params.get('user_id', None)
        content_id = query_params.get('content_id', None)

        page_no = query_params.get('page', 1)
        page_size = query_params.get("page_size", 10)

        # get contents according to the logged in user
        contents = self.get_contents(user, user_id, content_id)

        # paginate the results
        paged_contents = PaginationUtilities.paginate_results(contents, page_no, page_size)
        # serialize content
        serialized_contents = ContentSerializer(paged_contents, many=True).data

        response = {
            'success': True,
            'contents': serialized_contents
        }

        return Response(response)

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.is_superuser:
            response = ViewHelper.get_error_context(False, 'admin cannot create content')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

        post_data = RequestUtilities.get_post_data(request)

        if post_data is None:
            response = ViewHelper.get_error_context(False, 'Invalid params')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)
        # validate data to create a content
        self.validate_content_data(post_data)

        title = post_data.get('title', '')
        body = post_data.get('body', '')
        summary = post_data.get('summary', None)
        pdf = post_data.get('pdf', None)
        categories = post_data.get('categories', None)
        # get category instances list
        category_instance_list = self.get_categories(json.loads(categories))
        # create content
        content = self.create_content(user, title, body, summary, pdf, category_instance_list)

        response = {
            'success': True,
            'content': self.get_serialized_content(content)
        }

        return Response(response)

    def put(self, request, *args, **kwargs):
        user = request.user

        post_data = RequestUtilities.get_post_data(request)

        if post_data is None:
            response = ViewHelper.get_error_context(False, 'Invalid params')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

        content_id = post_data.get('id', '')
        title = post_data.get('title', '')
        body = post_data.get('body', '')
        summary = post_data.get('summary', None)
        pdf = post_data.get('pdf', None)
        categories = post_data.get('categories', None)

        if categories is not None:
            self.validate_categories(categories)

        content_instance = Content.get_content_with_id_or_raise_exception(content_id)
        # check if logged in user is content creator or admin
        if user.id == content_instance.user.id or user.is_superuser:
            # get category instances list
            category_instance_list = self.get_categories(json.loads(categories))
            # update the content data
            self.update_content(content_instance, title, body, summary, pdf, category_instance_list)

            response = {
                'success': True,
                'content': self.get_serialized_content(content_instance)
            }

            return Response(response)

        response = ViewHelper.get_error_context(False, 'only author or admin can edit content')

        raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user = request.user

        post_data = RequestUtilities.get_post_data(request)

        if post_data is None:
            response = ViewHelper.get_error_context(False, 'Invalid params')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

        content_id = post_data.get('id', None)

        if content_id is None:
            response = ViewHelper.get_error_context(False, 'send id in post params')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

        content_instance = Content.get_content_with_id_or_raise_exception(content_id)

        # check if logged in user is content creator or admin
        if user.id == content_instance.user.id or user.is_superuser:
            # delete content
            content_instance.delete()

            response = {
                'success': True
            }

            return Response(response)

        response = ViewHelper.get_error_context(False, 'only author or admin can delete content')

        raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

    def validate_categories(self, categories):
        """
        checks if the categories received is properly formatted into json string or not
        """
        try:
            json.loads(categories)
        except:
            response = ViewHelper.get_error_context(False, 'json decode error in categories')
            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

    def validate_content_data(self, data: dict) -> None:
        """
        validate the data required to create a content
        raises exception if data is missing
        """
        error_message = 'Required param {} missing in params'

        title = data.get('title', '')
        body = data.get('body', '')
        summary = data.get('summary', None)
        pdf = data.get('pdf', None)
        categories = data.get('categories', None)

        if categories is not None:
            self.validate_categories(categories)

        if title is None:
            missing_param = 'title'

        elif body is None:
            missing_param = 'body'

        elif summary is None:
            missing_param = 'summary'

        elif pdf is None:
            missing_param = 'pdf'

        elif categories is None or len(categories) <= 0:
            response = ViewHelper.get_error_context(False, 'Content must belong to at least one category')

            raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

        else:
            return

        response = ViewHelper.get_error_context(False, error_message.format(missing_param))

        raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)

    def get_categories(self, categories) -> list:
        """
        returns  list of category instances, based on give input list
        """
        instance_list = []

        for category in categories:
            category_instance, created = Category.objects.get_or_create(title=category)
            instance_list.append(category_instance)

        return instance_list

    def create_content(self, user, title, body, summary, pdf, category_instance_list) -> Content:
        """
        create content and returns the created content
        """
        content = Content(user=user,
                          title=title,
                          body=body,
                          summary=summary,
                          pdf=pdf)

        content.validate_date_and_raise_exception()
        content.save()

        content.categories.add(*category_instance_list)
        content.save()

        return content

    def update_content(self, content_instance, title, body, summary, pdf, category_instance_list) -> None:

        """
        updates the content data and saves it
        """

        content_instance.title = title if title else content_instance.title
        content_instance.body = body if body else content_instance.body
        content_instance.summary = summary if summary else content_instance.summary
        content_instance.pdf = pdf if pdf else content_instance.pdf

        if category_instance_list is not None:
            content_instance.categories.set(category_instance_list)

        content_instance.validate_date_and_raise_exception()

        content_instance.save()

    def get_serialized_content(self, content):
        """
        returns serialized content
        """
        return ContentSerializer(content, many=False).data

    def get_contents(self, user, user_id, content_id):
        """
        returns content based on logged in user
        if admin, sned every one's content
        else, send content of logged in user only
        """
        if user.is_superuser:
            if user_id is not None:
                contents = Content.objects.filter(user_id=user_id)

            elif content_id is not None:
                contents = Content.objects.filter(pk=content_id)

            else:
                contents = Content.objects.all()

        else:
            if content_id is not None:
                contents = Content.objects.filter(pk=content_id, user=user)

            else:
                contents = Content.objects.filter(user=user)

        return contents.prefetch_related('categories')


class SearchContentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        query_params = request.query_params

        search = query_params.get('search', None)

        page_no = query_params.get('page', 1)
        page_size = query_params.get("page_size", 10)

        if user.is_superuser:
            # if super user, send all user's content
            contents = Content.objects.all()
        else:
            # send only authenticated user's content
            contents = Content.objects.filter(user=user)

        if search is not None:
            # search content data, based on search key
            contents = contents.filter(Q(title__icontains=search) |
                                       Q(body__icontains=search) |
                                       Q(summary__icontains=search) |
                                       Q(categories__title__icontains=search)) \
                .prefetch_related('categories')\
                .distinct()

        # paginate content, based on page number
        paged_contents = PaginationUtilities.paginate_results(contents, page_no, page_size)

        # serialize content data
        serialized_contents = ContentSerializer(paged_contents, many=True).data

        response = {
            'success': True,
            'contents': serialized_contents
        }

        return Response(response)


class TokenView(APIView):

    def post(self, request, *args, **kwargs):
        post_data = RequestUtilities.get_post_data(request)

        email = post_data.get('email', None)
        password = post_data.get('password', None)

        # check if any user exists with given email
        user = User.get_user_by_email_or_none(email)

        # validate user's password
        if user is not None and user.check_password(password):
            # get user token
            token = ViewHelper.get_user_token(user)

            response = {
                'success': True,
                'token': token
            }

            return Response(response)

        response = ViewHelper.get_error_context(False, "Invalid email or password")
        raise CustomException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)


class ViewHelper:
    @staticmethod
    def get_error_context(success=False, error=''):
        return {
            'success': success,
            'error_message': error
        }

    @staticmethod
    def get_user_token(user):
        """
        returns user's token if already exist, else creates a token and return the token
        """
        token, created = Token.objects.get_or_create(user=user)

        return token.key
