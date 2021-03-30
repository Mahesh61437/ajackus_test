import json
from rest_framework import status as status_codes
from utilities.exception_utilities import JsonDecodeException


class RequestUtilities:

    @staticmethod
    def get_member_id_from_headers(request: object) -> str:
        return request.META.get('HTTP_X_MEMBER_ID')

    @staticmethod
    def get_post_data(request: object) -> dict:
        return request.data

    @staticmethod
    def fetch_body_or_raise_exception(request):
        try:
            return json.loads(request.body)
        except Exception as e:
            response = {
                'success': False,
                'error_message': f'{e.__class__.__name__} - {e.__str__()}'
            }
            raise JsonDecodeException(response, status_code=status_codes.HTTP_400_BAD_REQUEST)
