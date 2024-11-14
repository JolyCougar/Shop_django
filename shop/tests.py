from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Manufacturer, Product, Orders, Cart, CartItem


class CategoryModelTest(TestCase):
    def test_string_representation(self):
        category = Category(name="Electronics")
        self.assertEqual(str(category), category.name)


class ManufacturerModelTest(TestCase):
    def test_string_representation(self):
        manufacturer = Manufacturer(name="Samsung")
        self.assertEqual(str(manufacturer), manufacturer.name)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.manufacturer = Manufacturer.objects.create(name="Samsung")
        self.product = Product.objects.create(
            name="Galaxy S21",
            description="Latest Samsung smartphone",
            category=self.category,
            manufacturer=self.manufacturer,
            price=799.99,
            stock=50
        )

    def test_string_representation(self):
        self.assertEqual(str(self.product), self.product.name)

    def test_product_creation(self):
        self.assertEqual(self.product.price, 799.99)
        self.assertEqual(self.product.stock, 50)
        self.assertEqual(self.product.category.name, "Electronics")
        self.assertEqual(self.product.manufacturer.name, "Samsung")


class OrdersModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name="Electronics")
        self.manufacturer = Manufacturer.objects.create(name="Samsung")
        self.product = Product.objects.create(
            name="Galaxy S21",
            description="Latest Samsung smartphone",
            category=self.category,
            manufacturer=self.manufacturer,
            price=799.99,
            stock=50
        )
        self.order = Orders.objects.create(
            user=self.user,
            delivery_address="123 Test St",
            status="В обработке"
        )
        self.order.products.add(self.product)
        self.order.total_price = self.product.price
        self.order.save()

    def test_order_creation(self):
        self.assertEqual(self.order.user.username, 'testuser')
        self.assertEqual(self.order.delivery_address, "123 Test St")
        self.assertEqual(self.order.products.count(), 1)
        self.assertEqual(self.order.total_price, 799.99)


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user.username, 'testuser')


class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name="Electronics")
        self.manufacturer = Manufacturer.objects.create(name="Samsung")
        self.product = Product.objects.create(
            name="Galaxy S21",
            description="Latest Samsung smartphone",
            category=self.category,
            manufacturer=self.manufacturer,
            price=799.99,
            stock=50
        )
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_string_representation(self):
        self.assertEqual(str(self.cart_item), f'{self.product.name} (x{self.cart_item.quantity})')

    def test_cart_item_creation(self):
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(self.cart_item.product.name, "Galaxy S21")
