from django.urls import path, include
from .views import *

urlpatterns = [
    path('login', LoginOrRegisterUserView.as_view(), name="login_or_register_user"),
    path('content', UserContentView.as_view(), name="user_content"),
    path('content/search', SearchContentView.as_view(), name="search_content"),
    path('get_token', TokenView.as_view(), name="get_user_token"),
]

app_name = 'api'

