from django.urls import path

from .views import InterestOfferView

urlpatterns = [
    path('', InterestOfferView.as_view())
]
