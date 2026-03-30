# reviews/forms.py
from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Форма за създаване на отзив"""

    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} ★') for i in range(1, 6)]),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Заглавие на отзива'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Вашият коментар...'}),
        }
        labels = {
            'rating': 'Оценка',
            'title': 'Заглавие',
            'comment': 'Коментар',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = True
