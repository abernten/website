from django.urls import path

from .views import InterestOfferView, AcceptInterestView, DeclineInterestView

urlpatterns = [
    path('', InterestOfferView.as_view()),
    path('<int:id>/accept', AcceptInterestView.as_view()),
    path('<int:id>/decline', DeclineInterestView.as_view())
]
