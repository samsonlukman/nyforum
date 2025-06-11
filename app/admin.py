from django.contrib import admin
from .models import User, Event, Article, ArticleComment, ForumThread, ThreadReply, ThreadReplyLike
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Import base UserAdmin
from django.utils import timezone # Import timezone for actions

# Customize the default UserAdmin to display the new profile_pics field
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (('Profile Picture'), {'fields': ('profile_pics',)}),
    )
    list_display = BaseUserAdmin.list_display + ('profile_pics',)

admin.site.register(User, CustomUserAdmin)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'location', 'category')
    list_filter = ('category', 'date_time')
    search_fields = ('title', 'description', 'location')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at', 'created_at')
    list_filter = ('is_published', 'category', 'author')
    search_fields = ('title', 'content', 'tags')
    raw_id_fields = ('author',) # For large user bases
    date_hierarchy = 'published_at'
    actions = ['make_published', 'make_unpublished']

    def make_published(self, request, queryset):
        queryset.update(is_published=True, published_at=timezone.now())
    make_published.short_description = "Mark selected articles as published"

    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False, published_at=None)
    make_unpublished.short_description = "Mark selected articles as unpublished"

@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username')
    actions = ['approve_comments', 'disapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = "Disapprove selected comments"

@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at')
    list_filter = ('category', 'author')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)

@admin.register(ThreadReply)
class ThreadReplyAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at', 'parent_reply')
    list_filter = ('author', 'created_at')
    search_fields = ('content',)
    raw_id_fields = ('thread', 'author', 'parent_reply')

@admin.register(ThreadReplyLike) # Registered the new model
class ThreadReplyLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'reply', 'created_at')
    list_filter = ('user', 'reply')
    search_fields = ('user__username',)
    raw_id_fields = ('user', 'reply')


