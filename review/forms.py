from django import forms
from .models import Review, RatingStar


class ReviewForm(forms.ModelForm):
    rating = forms.ModelChoiceField(
        queryset=RatingStar.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Review
        fields = ['rating', 'text']


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']
