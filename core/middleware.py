from django.utils.deprecation import MiddlewareMixin
from core.models import Login

class CustomAuthMiddleware(MiddlewareMixin):
    """
    Custom middleware to attach the logged-in user object to the request
    based on the manual session 'user_id'.
    """
    def process_request(self, request):
        request.custom_user = None
        user_id = request.session.get('user_id')
        if user_id:
            try:
                request.custom_user = Login.objects.get(id=user_id, is_active=True)
            except Login.DoesNotExist:
                # If user doesn't exist or is inactive, clear the session
                request.session.flush()
