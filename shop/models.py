from decimal import Decimal
from django.utils.text import slugify
from django.db import models
from shopSite.settings import AUTH_USER_MODEL


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProductPathGenerator:
    @staticmethod
    def product_preview_directory_path(instance: "Product", filename: str) -> str:
        return f"products/product_{instance.pk}/preview/{filename}"

    @staticmethod
    def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
        return f"products/product_{instance.product.pk}/images/{filename}"

    @staticmethod
    def marketing_images_directory_path(instance: "Marketing", filename: str) -> str:
        return f"marketing/images/{filename}"


class Product(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    marketing_info = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    discounted_price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount = models.SmallIntegerField(default=0)
    new = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    attribute = models.TextField(null=False, blank=True, db_index=True)
    preview = models.ImageField(upload_to=ProductPathGenerator.product_preview_directory_path, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_all_images(self):
        images = []
        if self.preview:
            images.append({'url': self.preview.url, 'is_preview': True})
        images += [{'url': img.image.url, 'is_preview': False} for img in self.images.all()]
        return images

    def save(self, *args, **kwargs):
        # Рассчитываем цену со скидкой
        if self.discount > 0:
            discount_amount = self.price * (self.discount / Decimal(100))
            self.discounted_price = self.price - discount_amount
        else:
            self.discounted_price = self.price

        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=ProductPathGenerator.product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT)
    delivery_address = models.TextField(null=False)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='В обработке')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    promo = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'Order #{self.id} by {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} (x{self.quantity})'


class Cart(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} (x{self.quantity})'


class Marketing(models.Model):
    name = models.CharField("name", max_length=100)
    image = models.ImageField(upload_to=ProductPathGenerator.marketing_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)
    description_full = models.TextField(null=False, blank=True, db_index=True)
    url = models.SlugField(max_length=130, unique=True)
    products = models.ManyToManyField(Product, related_name='promotions', blank=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.url:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
