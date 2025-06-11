from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import User, Event, Article, ArticleComment, ForumThread, ThreadReply, ThreadReplyLike # Added Candidate model
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileUpdateForm,
    ArticleForm, ForumThreadForm, ArticleCommentForm, ThreadReplyForm, ContactForm
)


def home_view(request):
    """
    Home page view displaying a brief intro, latest blog posts,
    forum discussions, and upcoming events.
    """
    # Fetch latest articles (only published ones)
    latest_articles = Article.objects.filter(is_published=True).order_by('-published_at')[:3]

    # Fetch latest forum threads (order by most recent activity)
    # This might require more complex queries in a real app to get "trending"
    latest_forum_threads = ForumThread.objects.annotate(
        num_replies=Count('replies')
    ).order_by('-updated_at')[:3]

    # Fetch upcoming events
    upcoming_events = Event.objects.filter(date_time__gte=timezone.now()).order_by('date_time')[:2]

    # Placeholder for candidate (assuming one candidate for now)
    # You might fetch this from a Candidate model if you implement one
    # from .models import Candidate
    # candidate = Candidate.objects.first() # Or filter by active candidate

    context = {
        'latest_articles': latest_articles,
        'latest_forum_threads': latest_forum_threads,
        'upcoming_events': upcoming_events,
        'candidate_name': "[Aspiring Presidential Candidate Name]", # Placeholder
        'candidate_bio_short': "Dedicated to progress, unity, and a prosperous Nigeria for all young people.", # Placeholder
        # 'candidate': candidate, # Uncomment if you have a Candidate model instance
    }
    return render(request, 'app/home.html', context)

def olajide_filani(request):
    return render(request, "app/olajide_filani.html")

def donate(request):
    return render(request, "app/donate.html")

def faq(request):
    return render(request, "app/faq.html")

def privacy_policy(request):
    return render(request, "app/privacy.html")

def terms_of_service(request):
    return render(request, "app/terms.html")

def about_view(request):
    """
    About Us page view.
    """
    return render(request, 'app/about.html')

class UserLoginView(LoginView):
    """
    Handles user login. Uses Django's built-in LoginView.
    """
    template_name = 'app/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True # Redirects if user is already logged in

    def get_success_url(self):
        # Redirect to profile page after successful login
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})

def register_view(request):
    """
    Handles user registration.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES) # Include request.FILES for profile_pics
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in after registration
            messages.success(request, 'Registration successful! Welcome to the forum.')
            return redirect('profile', username=user.username)
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'app/register.html', {'form': form})

def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    return render(request, "app/home.html")

def forum_list_view(request):
    """
    Displays a list of forum threads.
    Includes search and category filtering.
    """
    threads = ForumThread.objects.annotate(num_replies=Count('replies')).all().order_by('-updated_at')
    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        threads = threads.filter(title__icontains=query)
    if category and category != 'all':
        threads = threads.filter(category=category)

    context = {
        'threads': threads,
        'current_query': query,
        'current_category': category,
        'categories': ForumThread.category.field.choices, # Get choices for dropdown
    }
    return render(request, 'app/forum_list.html', context)

def forum_detail_view(request, thread_id):
    """
    Displays a single forum thread and its replies.
    Allows authenticated users to post replies.
    """
    thread = get_object_or_404(ForumThread, id=thread_id)
    replies = thread.replies.all() # Fetch all replies for the thread
    
    initial_data = {}
    if request.method == 'POST':
        # Check if the post is a reply submission
        if 'submit_reply' in request.POST:
            reply_form = ThreadReplyForm(request.POST)
            if reply_form.is_valid():
                new_reply = reply_form.save(commit=False)
                new_reply.thread = thread
                new_reply.author = request.user
                new_reply.save()
                messages.success(request, 'Your reply has been posted!')
                return redirect('forum_detail', thread_id=thread.id)
            else:
                messages.error(request, 'Failed to post reply. Please check your input.')
        # If it's a like/unlike action, it will be handled by the AJAX view
    
    # Initialize forms for GET request or if POST failed
    reply_form = ThreadReplyForm(initial=initial_data)

    context = {
        'thread': thread,
        'replies': replies,
        'reply_form': reply_form,
    }
    return render(request, 'app/forum_detail.html', context)

def article_list_view(request):
    """
    Displays a list of articles.
    Includes search and category/tag filtering.
    """
    articles = Article.objects.filter(is_published=True).order_by('-published_at')
    query = request.GET.get('q')
    category = request.GET.get('category')
    tag = request.GET.get('tag')

    if query:
        articles = articles.filter(title__icontains=query)
    if category and category != 'all':
        articles = articles.filter(category=category)
    if tag:
        articles = articles.filter(tags__icontains=tag) # Simple tag search

    context = {
        'articles': articles,
        'current_query': query,
        'current_category': category,
        'current_tag': tag,
        'categories': Article.category.field.choices,
        # You might fetch a list of all unique tags here for the filter dropdown
        # 'tags': Article.objects.values_list('tags', flat=True).distinct()
    }
    return render(request, 'app/article_list.html', context)

def article_detail_view(request, article_id):
    """
    Displays a single article and its comments.
    Allows authenticated users to post comments.
    """
    article = get_object_or_404(Article, id=article_id, is_published=True)
    comments = article.comments.filter(is_approved=True).order_by('created_at')

    if request.method == 'POST':
        comment_form = ArticleCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, 'Comment posted!')
            return redirect('article_detail', article_id=article.id)
        else:
            messages.error(request, 'Failed to post comment. Please correct the errors.')
    else:
        comment_form = ArticleCommentForm()

    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'app/article_detail.html', context)

@login_required
def write_post_view(request):
    """
    Allows authenticated users to write a new article or forum thread.
    """
    article_form = ArticleForm()
    forum_thread_form = ForumThreadForm()

    if request.method == 'POST':
        post_type = request.POST.get('post_type') # 'article' or 'forum_thread'

        if post_type == 'article':
            article_form = ArticleForm(request.POST, request.FILES)
            if article_form.is_valid():
                new_article = article_form.save(commit=False)
                new_article.author = request.user
                # Admin will review is_published. If not checked, it defaults to False.
                new_article.save()
                if request.user.is_superuser:
                    messages.success(request, 'Article posted successfully.')
                    return redirect('article_detail', article_id=new_article.id)
                else:
        # Send flag to template to show modal instead of redirect
                    context = {
                        'article_form': ArticleForm(),
                        'forum_thread_form': ForumThreadForm(),
                        'show_review_modal': True,
                    }
                    return render(request, 'app/write_post.html', context)
            else:
                messages.error(request, 'Failed to submit article. Please correct errors.')
        elif post_type == 'forum_thread':
            forum_thread_form = ForumThreadForm(request.POST, request.FILES)
            if forum_thread_form.is_valid():
                new_thread = forum_thread_form.save(commit=False)
                new_thread.author = request.user
                new_thread.save()
                messages.success(request, 'Your forum thread has been created!')
                return redirect('forum_detail', thread_id=new_thread.id)
            else:
                messages.error(request, 'Failed to submit forum thread. Please correct errors.')
        else:
            messages.error(request, 'Invalid post type specified.')

    context = {
        'article_form': article_form,
        'forum_thread_form': forum_thread_form,
    }
    return render(request, 'app/write_post.html', context)

def chatbot_view(request):
    """
    Chatbot page view. This is a placeholder for actual AI integration.
    """
    return render(request, 'app/chatbot.html')

def contact_view(request):
    """
    Handles the contact us form.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            try:
                # This is a placeholder for sending an actual email
                # In a real app, ensure settings.EMAIL_HOST, etc., are configured
                # and use a more robust email sending library like Anymail.
                send_mail(
                    f'NYF Contact: {subject} from {name} ({email})',
                    message,
                    settings.DEFAULT_FROM_EMAIL, # Sender email (configured in settings.py)
                    [settings.CONTACT_EMAIL],   # Recipient email (your forum's contact email)
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('contact')
            except Exception as e:
                messages.error(request, f'There was an error sending your message: {e}')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = ContactForm()
    return render(request, 'app/contact.html', {'form': form})

def events_view(request):
    """
    Displays a list of upcoming and past events.
    """
    upcoming_events = Event.objects.filter(date_time__gte=timezone.now()).order_by('date_time')
    past_events = Event.objects.filter(date_time__lt=timezone.now()).order_by('-date_time')

    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        upcoming_events = upcoming_events.filter(title__icontains=query)
        past_events = past_events.filter(title__icontains=query)
    if category and category != 'all':
        upcoming_events = upcoming_events.filter(category=category)
        past_events = past_events.filter(category=category)

    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'current_query': query,
        'current_category': category,
        'categories': Event.category.field.choices,
    }
    return render(request, 'app/events.html', context)

@login_required
def profile_view(request, username):
    """
    Displays a user's profile, including their posts, comments, and discussions.
    Allows the user to edit their profile if they are the owner.
    """
    profile_owner = get_object_or_404(User, username=username)
    is_owner = (request.user == profile_owner)

    # Fetch data for tabs
    user_articles = profile_owner.articles.all().order_by('-created_at')
    user_forum_threads = profile_owner.forum_threads.all().order_by('-created_at')
    user_article_comments = profile_owner.article_comments.all().order_by('-created_at')
    user_thread_replies = profile_owner.thread_replies.all().order_by('-created_at')

    edit_profile_form = None
    if is_owner:
        if request.method == 'POST':
            edit_profile_form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile_owner)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile', username=profile_owner.username)
            else:
                messages.error(request, 'Failed to update profile. Please correct the errors.')
        else:
            edit_profile_form = UserProfileUpdateForm(instance=profile_owner)

    context = {
        'profile_owner': profile_owner,
        'is_owner': is_owner,
        'user_articles': user_articles,
        'user_forum_threads': user_forum_threads,
        'user_article_comments': user_article_comments,
        'user_thread_replies': user_thread_replies,
        'edit_profile_form': edit_profile_form,
    }
    return render(request, 'app/profile.html', context)

@login_required
def like_reply_view(request, reply_id):
    """
    Handles liking and unliking of forum replies via AJAX.
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Must be an AJAX request'}, status=400)

    reply = get_object_or_404(ThreadReply, id=reply_id)
    user = request.user

    if ThreadReplyLike.objects.filter(user=user, reply=reply).exists():
        # User already liked, so unlike
        ThreadReplyLike.objects.filter(user=user, reply=reply).delete()
        liked = False
        message = 'Reply unliked.'
    else:
        # User hasn't liked, so like
        ThreadReplyLike.objects.create(user=user, reply=reply)
        liked = True
        message = 'Reply liked.'

    # Return updated like count
    like_count = reply.likes.count()
    return JsonResponse({
        'liked': liked,
        'like_count': like_count,
        'message': message
    })

