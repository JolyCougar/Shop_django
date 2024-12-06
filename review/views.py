# from django.views.generic.edit import FormView
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from .models import Product, Review
# from .forms import ReviewForm

# class AddReviewView(FormView):
#     form_class = ReviewForm
#
#     def form_valid(self, form):
#         product_id = self.kwargs.get('product_id')
#         product = get_object_or_404(Product, id=product_id)
#         user = self.request.user
#
#         # Проверка на дублирующий отзыв
#         if Review.objects.filter(author=user, product=product).exists():
#             messages.error(self.request, 'Вы уже оставили отзыв для этого товара.')
#             return redirect('shop:product-detail', pk=product.id)
#
#         # Сохранение нового отзыва
#         review = form.save(commit=False)
#         review.author = user
#         review.product = product
#         review.save()
#         messages.success(self.request, 'Ваш отзыв успешно добавлен!')
#         return redirect('shop:product-detail', pk=product.id)
#
#     def form_invalid(self, form):
#         product_id = self.kwargs.get('product_id')
#         messages.error(self.request, 'Ошибка отправки формы. Проверьте введенные данные.')
#         return redirect('shop:product-detail', pk=product_id)