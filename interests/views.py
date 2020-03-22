from django.shortcuts import render

from .models import InterestOffer
from erntehelfer.models import CitizenProfile, CompanyProfile

class InterestOfferView(View):

    def get(self, request):
        if request.user.groups.filter(name__in=['Helfer']).exists():
            # Citizen
            citizen = CitizenProfile.objects.get(owner__id=request.user.id)
            interested = InterestOffer.objects.filter(citizen__id=citizen.id)
            return render(request, 'interests/citizen.html', {
                'citizen': citizen,
                'interested': interested
            })
        else:
            company = CompanyProfile.objects.get(owner__id=request.user.id)
            interested = InterestOffer.objects.filter(task__company__id=company.id)

            # Company
            return render(request,'interests/company.html', {
                'company': company,
                'interested': interested
            })
