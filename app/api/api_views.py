# your_app/views.py
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

class FacebookPostProxyAPIView(APIView):
    def get(self, request):
        page_id = settings.FACEBOOK_PAGE_ID
        access_token = settings.FACEBOOK_PAGE_ACCESS_TOKEN

        # The URL to the Facebook Graph API for page posts
        url = f"https://graph.facebook.com/v18.0/{page_id}/posts"

        # Parameters to get specific fields from the posts, like the message
        params = {
            'fields': 'message,created_time',
            'access_token': access_token,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # Raise an exception for bad status codes

            # Filter out posts without a 'message' field
            posts_data = [
                {'content': post['message'], 'created_at': post['created_time']} 
                for post in response.json().get('data', []) if 'message' in post
            ]

            # Return the filtered data
            return Response(posts_data)

        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=500)