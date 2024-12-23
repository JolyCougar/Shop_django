from django.views.generic import CreateView, UpdateView
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Review, Rating, RatingStar
from .forms import ReviewForm, ReplyForm


class AddReviewView(CreateView):
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, id=self.kwargs.get('product_id'))

        existing_review = Review.objects.filter(product=product, author=self.request.user).first()

        context['existing_review'] = existing_review

        return context

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs.get('product_id'))
        existing_review = Review.objects.filter(product=product, author=request.user).first()

        if existing_review:
            return JsonResponse({
                'success': False,
                'message': 'Вы уже оставили отзыв для этого продукта.'},
                status=400
            )

        form = self.form_class(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.product = product
            review.save()
            rating_value = form.cleaned_data['rating']

            if rating_value:
                rating = Rating(user=request.user, star=rating_value, product=product)
                rating.save()

            return redirect('shop:product-detail', pk=review.product.id)

        return JsonResponse({'success': False, 'message': 'Неверные данные формы.'}, status=400)


class AddReplyView(CreateView):
    form_class = ReplyForm

    def post(self, request, *args, **kwargs):
        review = get_object_or_404(Review, id=kwargs.get('review_id'))
        form = self.form_class(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.product = review.product
            reply.parent = review
            reply.save()

            return redirect('shop:product-detail', pk=review.product.id)

        return JsonResponse({
            'success': False,
            'message': 'Неверные данные формы.',
            'errors': form.errors
        }, status=400)


class EditReviewView(UpdateView):
    model = Review
    form_class = ReviewForm

    def get_object(self, queryset=None):
        review_id = self.kwargs.get('pk')
        return get_object_or_404(Review, pk=review_id)

    def get(self, request, *args, **kwargs):
        review = self.get_object()

        if review.author != request.user:
            raise PermissionDenied("Вы не можете редактировать этот отзыв.")

        return JsonResponse({
            'success': True,
            'review': {
                'text': review.text,
                'rating': review.rating.id,
            }
        })

    def post(self, request, *args, **kwargs):
        review = self.get_object()
        if review.author != request.user:
            raise PermissionDenied("Вы не можете редактировать этот отзыв.")

        form = self.form_class(request.POST, instance=review)

        if form.is_valid():
            rating_id = request.POST.get('rating')
            if rating_id:
                rating = get_object_or_404(RatingStar, pk=rating_id)
                review.rating = rating

                rating_instance, created = Rating.objects.get_or_create(
                    user=review.author,
                    product=review.product,
                    defaults={'star': rating}
                )

                if not created:
                    rating_instance.star = rating
                    rating_instance.save()
            updated_review = form.save()

            return redirect('shop:product-detail', pk=review.product.id)
        return JsonResponse({'success': False, 'message': 'Неверные данные формы.'})
