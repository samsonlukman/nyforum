from django.db import models
from django.contrib.auth.models import AbstractUser # For custom user model if needed, or use default User
from django.utils import timezone

class User(AbstractUser):

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_pics = models.ImageField(upload_to='profile_pics/', blank=True, null=True,
                                     help_text="User's profile picture.")

    def __str__(self):
        return f"{self.username} | {self.first_name} {self.last_name} | {self.email} "



class Event(models.Model):
    """
    Represents an upcoming youth political event, webinar, or town hall.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255) # E.g., "Online Webinar (Zoom)", "Abuja Conference Center"
    category = models.CharField(
        max_length=50,
        choices=[
            ('webinar', 'Webinar'),
            ('town_hall', 'Town Hall'),
            ('workshop', 'Workshop'),
            ('conference', 'Conference'),
            ('other', 'Other'),
        ],
        default='other'
    )
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    organizer = models.CharField(max_length=100, blank=True, null=True)
    registration_link = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time'] # Order events by date and time

    def __str__(self):
        return self.title

class Article(models.Model):
    """
    Represents a blog post or article.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('elections', 'Elections'),
            ('leadership', 'Leadership'),
            ('economy', 'Economy'),
            ('youth_empowerment', 'Youth Empowerment'),
            ('general', 'General'),
        ],
        default='general'
    )
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags (e.g., policy, governance)")
    is_published = models.BooleanField(default=False) # For moderation queue
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at'] # Latest articles first

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} | {self.author}"

class ArticleComment(models.Model):
    """
    Represents a comment on an article.
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True) # For moderation

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.article.title[:20]}'

class ForumThread(models.Model):
    """
    Represents a discussion thread in the forum.
    """
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True) # Initial post content
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_threads')
    image = models.ImageField(upload_to='forum/', blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('politics', 'Politics & Governance'),
            ('youth_empowerment', 'Youth Empowerment'),
            ('events_announcements', 'Events & Announcements'),
            ('general', 'General Discussion'),
        ],
        default='general'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at'] # Most recently active threads first

    def __str__(self):
        return self.title

class ThreadReply(models.Model):
    """
    Represents a reply or comment within a forum thread.
    """
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='thread_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children') # For nested replies

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Thread Replies"

    def __str__(self):
        return f'Reply by {self.author.username} to {self.thread.title[:20]}'

class ThreadReplyLike(models.Model):
    """
    Represents a 'like' action on a ThreadReply by a User.
    This model allows a user to like a reply only once.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_replies')
    reply = models.ForeignKey(ThreadReply, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can like a specific reply only once
        unique_together = ('user', 'reply')
        ordering = ['-created_at'] # Latest likes first

    def __str__(self):
        return f'{self.user.username} likes reply {self.reply.id}'