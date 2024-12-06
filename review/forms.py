from django import forms
from .models import Review, RatingStar

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']

    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Напишите ваш отзыв...',
            'rows': 4,
            'style': 'width: 100%;',
        }),
        label="Текст отзыва"
    )
    rating = forms.ModelChoiceField(
        queryset=RatingStar.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Оценка"
    )
