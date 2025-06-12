from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Article, ForumThread, ArticleComment, ThreadReply, Event
from django.core.exceptions import ValidationError
from django.contrib.auth.backends import ModelBackend

class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration, extending Django's built-in UserCreationForm.
    Includes custom fields from the User model (phone_number, bio, profile_pics).
    """
    phone_number = forms.CharField(max_length=15, required=False,
                                   widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Optional: Your phone number'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors min-h-[120px]', 'placeholder': 'Optional: Tell us about yourself...'}), required=False)
    profile_pics = forms.ImageField(required=False,
                                    widget=forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors bg-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-green file:text-white hover:file:bg-secondary-green cursor-pointer'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_pics',)
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Your last name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'your@example.com'}),
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Choose a unique username'}),
        }

    # Ensure email is required and unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(username=self.cleaned_data.get('username')).exists():
            raise ValidationError("A user with that email already exists.")
        return email

class UserLoginForm(AuthenticationForm):
    """
    Form for user login.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Your username'}),
        label="Username or Email" # Change label for better UX, though backend still uses username
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Your password'})
    )

    # Allow login with either username or email
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Try to authenticate with username first
            user = ModelBackend().authenticate(request=self.request, username=username, password=password)
            if user:
                self.user_cache = user
                return self.cleaned_data
            
            # If username fails, try with email
            try:
                user_by_email = User.objects.get(email=username)
                user = ModelBackend().authenticate(request=self.request, username=user_by_email.username, password=password)
            except User.DoesNotExist:
                pass # Continue to raise error if no user found

            if user:
                self.user_cache = user
            else:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        return self.cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_pics']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Your last name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'your@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Optional: Your phone number'}),
            'bio': forms.Textarea(attrs={'class': 'w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors min-h-[120px]', 'placeholder': 'Tell us about yourself...'}),
            'profile_pics': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors bg-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-green file:text-white hover:file:bg-secondary-green cursor-pointer'}),
        }

class ArticleForm(forms.ModelForm):
    """
    Form for creating/editing articles.
    Now includes 'slug' field.
    """
    class Meta:
        model = Article
        # Add 'author' to the fields list so it appears in the form
        fields = ['title', 'slug', 'author', 'content', 'featured_image', 'category', 'tags', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Enter your article title here'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed', 'readonly': 'readonly'}),
            'author': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors bg-white'}), # Add widget for author
            'content': forms.Textarea(attrs={'class': 'w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors min-h-[300px]', 'placeholder': 'Write your article content here. You can use Markdown or basic HTML...'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors bg-white'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'e.g., Elections, Leadership, Policy'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors bg-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-green file:text-white hover:file:bg-secondary-green cursor-pointer'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-primary-green rounded-md focus:ring-primary-green mr-2', 'style': 'color: var(--primary-green);'})
        }

class ForumThreadForm(forms.ModelForm):
    """
    Form for creating/editing forum threads.
    """
    class Meta:
        model = ForumThread
        fields = ['title', 'content', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Enter your thread title here'}),
            'content': forms.Textarea(attrs={'class': 'w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors min-h-[150px]', 'placeholder': 'Write your initial post content...'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors bg-white'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors bg-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-green file:text-white hover:file:bg-secondary-green cursor-pointer'}),
        }

class ArticleCommentForm(forms.ModelForm):
    """
    Form for adding comments to articles.
    """
    class Meta:
        model = ArticleComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors min-h-[100px]', 'placeholder': 'Join the discussion...'}),
        }

class ThreadReplyForm(forms.ModelForm):
    """
    Form for adding replies to forum threads.
    """
    class Meta:
        model = ThreadReply
        fields = ['content', 'parent_reply']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors min-h-[100px]', 'placeholder': 'Write your reply...'}),
            'parent_reply': forms.HiddenInput(), # Hidden field for nested replies
        }
        labels = {
            'content': '' # No label for content to keep it clean in UI
        }

class ContactForm(forms.Form):
    """
    Form for the contact us page.
    """
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'your@example.com'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors', 'placeholder': 'Inquiry about...'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:border-primary-green transition-colors min-h-[150px]', 'placeholder': 'Type your message here...'}), required=True)

