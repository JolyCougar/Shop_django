from django.urls import path
from .views import AddReviewView, AddReplyView, EditReviewView

app_name = 'review'

urlpatterns = [
    path('<int:product_id>/add-review/', AddReviewView.as_view(), name='add_review'),
    path('<int:review_id>/add-reply/', AddReplyView.as_view(), name='add_reply'),
    path('<int:pk>/edit/', EditReviewView.as_view(), name='edit_review'),

]
