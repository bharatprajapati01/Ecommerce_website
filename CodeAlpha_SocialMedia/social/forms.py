from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, Comment, Post, Profile


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name


class PostForm(forms.ModelForm):
    category = CategoryChoiceField(
        queryset=Category.objects.filter(parent__isnull=False)
        .select_related("parent")
        .order_by("parent__order", "order"),
        required=False,
        empty_label="Choose a category",
    )

    class Meta:
        model = Post
        fields = ["content", "image", "category"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "What's on your mind?", "maxlength": 500}
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {"content": forms.TextInput(attrs={"placeholder": "Write a comment...", "maxlength": 300})}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar"]
        widgets = {"bio": forms.TextInput(attrs={"placeholder": "Tell people about yourself", "maxlength": 160})}
