from django.views.generic import CreateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Product, Review, Rating
from .forms import ReviewForm, ReplyForm


class AddReviewView(CreateView):
    form_class = ReviewForm

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs.get('product_id'))
        form = self.form_class(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.product = product
            review.save()

            rating_value = form.cleaned_data['rating']
            rating = Rating(user=request.user, star=rating_value, product=product)
            rating.save()

            return JsonResponse({'success': True})
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
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'message': 'Неверные данные формы.'}, status=400)
