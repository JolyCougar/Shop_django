from django.db import models
from account.models import CustomUser
from shop.models import Product


class RatingStar(models.Model):
    value = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f'{self.value}'


class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.star} - {self.product.name}"

    class Meta:
        unique_together = ('user', 'product')


class Review(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.ForeignKey(RatingStar, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв {self.author.username} для {self.product.name} - Рейтинг: {self.rating}'
