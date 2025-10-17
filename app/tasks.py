# your_app/tasks.py
from celery import shared_task
import requests
import openai
from django.conf import settings

@shared_task
def generate_and_post_to_facebook():
    client = openai.OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
    )

    # This part generates the post content
    messages = [{
        "role": "system",
        "content": "You are a conversational Islamic Q&A bot. Generate a short, engaging Islamic post about a topic like faith, prayer, or a verse from the Quran. The post should be concise and end with a question to encourage engagement."
    }]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        max_tokens=150,
    )
    post_content = response.choices[0].message.content

    # This part posts to Facebook
    page_id = settings.FACEBOOK_PAGE_ID
    access_token = settings.FACEBOOK_PAGE_ACCESS_TOKEN

    url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
    payload = {
        'message': post_content,
        'access_token': access_token,
    }
    requests.post(url, data=payload)