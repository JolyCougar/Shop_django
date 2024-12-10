from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser
from shop.models import Product, Manufacturer, Category, Marketing


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    bio = forms.CharField(max_length=500, required=False, widget=forms.Textarea)
    agreement_accepted = forms.BooleanField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'agreement_accepted')


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Current Password'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'New Password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'marketing_info', 'category', 'manufacturer', 'price', 'discount', 'new',
                  'archived', 'stock', 'attribute', 'preview']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля.")
        return price

    def clean_discount(self):
        discount = self.cleaned_data.get('discount')
        if discount < 0 or discount > 100:
            raise forms.ValidationError("Скидка должна быть в пределах от 0 до 100.")
        return discount


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Manufacturer.objects.filter(name=name).exists():
            raise forms.ValidationError("Такой производитель уже существует.")
        return name


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("Такая категория уже существует.")
        return name


class MarketingForm(forms.ModelForm):
    class Meta:
        model = Marketing
        fields = ['name', 'image', 'description', 'description_full', 'url', 'products', 'archived']
        widgets = {
            'products': forms.CheckboxSelectMultiple(),
        }

    def clean_url(self):
        url = self.cleaned_data.get('url')
        if Marketing.objects.filter(url=url).exists():
            raise forms.ValidationError("URL должен быть уникальным.")
        return url
