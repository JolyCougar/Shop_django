from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount = models.SmallIntegerField(default=0)
    archived = models.BooleanField(default=False)
    stock = models.PositiveIntegerField(default=0)
    preview = models.ImageField(upload_to=product_preview_directory_path, blank=True, null=True)

    def __str__(self):
        return self.name


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.name} (x{self.quantity})'
