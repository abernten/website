from django.db.models import Q
from django.views import View
from django.shortcuts import render,redirect
from django.contrib import messages

from .models import InterestOffer
from erntehelfer.models import CitizenProfile, CompanyProfile

class InterestOfferView(View):

    def get(self, request):
        if request.user.groups.filter(name__in=['Helfer']).exists():
            # Citizen
            citizen = CitizenProfile.objects.get(owner__id=request.user.id)
            interested = InterestOffer.objects.filter(citizen__id=citizen.id, task__done=False)
            return render(request, 'interests/citizen.html', {
                'citizen': citizen,
                'interested': interested
            })
        else:
            company = CompanyProfile.objects.get(owner__id=request.user.id)
            interested = InterestOffer.objects.filter(Q(task__company__id=company.id), Q(task__done=False), Q(state=0) | Q(state=1))

            # Company
            return render(request,'interests/company.html', {
                'company': company,
                'interested': interested
            })

class AcceptInterestView(View):

    def get(self, request, id):
        if request.user.groups.filter(name__in=['Betrieb']).exists():
            # Company
            interested = InterestOffer.objects.get(pk=id)
            interested.state = 1
            interested.save()

            messages.success(request, 'Die Kontaktdaten werden an den Interessenten versendet!',extra_tags='alert-success')
            return redirect('/interests')
        else:
            return redirect('/dashboard')

class DeclineInterestView(View):

    def get(self, request, id):
        if request.user.groups.filter(name__in=['Betrieb']).exists():
            # Company
            interested = InterestOffer.objects.get(pk=id)
            interested.state = 2
            interested.save()

            messages.success(request, 'Die Kontaktdaten werden an den Interessenten versendet!',extra_tags='alert-success')
            return redirect('/interests')
        else:
            return redirect('/dashboard')

