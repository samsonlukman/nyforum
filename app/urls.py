from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('olajide-filani/', views.olajide_filani, name='olajide_filani'),
    path('donate/', views.donate, name='donate'),
    path('register/', views.register_view, name='register'),
    path('accounts/login/', views.UserLoginView.as_view(), name='login'),
    path("accounts/logout/", views.logout_view, name="logout"),

    path('forum/', views.forum_list_view, name='forum_list'),
    path('forum/<int:thread_id>/', views.forum_detail_view, name='forum_detail'),
    path('forum/reply/<int:reply_id>/like/', views.like_reply_view, name='like_reply'), # AJAX endpoint

    path('blog/', views.article_list_view, name='article_list'),
    path('blog/<slug:slug>/', views.article_detail_view, name='article_detail'), # Changed to slug


    path('write-post/', views.write_post_view, name='write_post'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('api/chatbot/', views.chatbot_api_view, name='chatbot_api'), 
    path('contact/', views.contact_view, name='contact'),
    path('events/', views.events_view, name='events'),
    path('event/<int:event_id>/', views.view_event_pdf, name='view_event_pdf'),
    path('events/<int:id>/<slug:slug>/', views.event_detail_view, name='event_detail'),

    path('faq/', views.faq, name='faq'),
    path('terms-of-service/', views.terms_of_service, name='terms'),
    path('privacy-policy/', views.privacy_policy, name='privacy'),

    path('profile/<str:username>/', views.profile_view, name='profile'),
]