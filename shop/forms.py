from django import forms
from django.forms.models import inlineformset_factory
from .models import Product, Manufacturer, Category, Marketing, ProductImage, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'marketing_info', 'category', 'manufacturer',
                  'price', 'discount', 'new', 'archived', 'stock', 'attribute', 'preview']

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


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'description']


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True
)


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


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "complete"]
