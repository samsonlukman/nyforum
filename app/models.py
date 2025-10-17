from django.db import models
from django.contrib.auth.models import AbstractUser # For custom user model if needed, or use default User
from django.utils import timezone
from django.utils.text import slugify # Import slugify
from django.db.models.signals import pre_save # Import pre_save signal
from django.dispatch import receiver # Import receiver decorator
from django.urls import reverse

class User(AbstractUser):

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_pics = models.ImageField(upload_to='profile_pics/', blank=True, null=True,
                                     help_text="User's profile picture.")

    def __str__(self):
        return f"{self.username} | {self.first_name} {self.last_name} | {self.email} "



class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField()
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
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
    pdf_file = models.FileField(upload_to='event_pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', args=[self.id, self.slug])


class Article(models.Model):
    """
    Represents a blog post or article.
    Added 'slug' field for clean URLs.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True) # TEMPORARILY ADD null=True
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    image = models.ImageField(upload_to='articles/', blank=True, null=True) # This seems duplicate with featured_image, consider removing one.
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
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} | {self.author}"

# Signal to auto-generate slug for Article
@receiver(pre_save, sender=Article)
def generate_article_slug(sender, instance, *args, **kwargs):
    if not instance.slug: # Only generate if slug is not already set
        base_slug = slugify(instance.title)
        # Ensure slug is unique, append a number if necessary
        unique_slug = base_slug
        num = 1
        while Article.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{num}"
            num += 1
        instance.slug = unique_slug

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