from django.db.models import Q
from django.views import View
from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.mail import send_mail

from django.core.paginator import Paginator

from .models import InterestOffer
from erntehelfer.models import CitizenProfile, CompanyProfile

class InterestOfferView(View):

    def get(self, request):
        if request.user.groups.filter(name__in=['Helfer']).exists():
            # Citizen
            citizen = CitizenProfile.objects.get(owner__id=request.user.id)
            interested = InterestOffer.objects.filter(Q(citizen__id=citizen.id), Q(task__done=False), Q(state=0) | Q(state=1))
            return render(request, 'interests/citizen.html', {
                'citizen': citizen,
                'interested': interested
            })
        else:
            company = CompanyProfile.objects.get(owner__id=request.user.id)
            interested = InterestOffer.objects.filter(Q(task__company__id=company.id), Q(task__done=False), Q(state=0) | Q(state=1))

            # Order by created_at
            interested = interested.order_by('created_at')

            # Task paginator
            paginator = Paginator(interested, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            # Company
            return render(request,'interests/company.html', {
                'helper_count': paginator.count,
                'num_pages': paginator.num_pages,
                'page_obj': page_obj,
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

            company = interested.task.company
            citizen = interested.citizen

            #send_mail('Bestätigung ihres Hilfeangebotes für: ' + interested.task.title,
            #           'Hallo ' + citizen.owner.first_name + ' ' +  citizen.owner.last_name + '. \n' +
            #           'Vielen Dank, dass du Abernten.de nutzt! \n' +
            #           #</br>
            #           'Dein Hilfeangebot vom ' + interested.created_at + ' wurde akzeptiert. \n' +
            #           'Hier findest du die Kontakt Daten des Hilfesuchenden: \n' +
            #           company.company_name + '\n' + 'Tel: ' + company.owner.phone + '\n' + 'Mail: ' + company.owner.email + '\n' + company.street + '\n' + company.zip_code + '\n' + company.city + '\n' +
            #           #</br>
            #           'Bitte setze dich mit der Person in Verbindung, um genaueres wie Einsatzzeitraum und Bezahlung zu klären. \n' +
            #           #</br>
            #           'Vielen Dank und Viele Grüße \n'
            #           #</br>
            #           'Dein Abernten-Team \n',
            #           'no-reply@abernten.de',
            #           [citizen.owner.email]
            #         )

            # send_mail('Bestätigung eines Hilfeangebots für: ' + interested.task.title ,
            #           'Hallo ' + company.company_name + '. \n' +
            #           'Vielen Dank, dass du Abernten.de nutzt! \n' +
            #           #</br>
            #           'Du hast das Hilfeangebot von ' + citizen.owner.first_name + ' ' + citizen.owner.last_name + ' akzeptiert. \n' +
            #           'Hier findest du die Kontakt Daten des Helfers: \n' +
            #           citizen.owner.first_name + ' ' + citizen.owner.last_name + '\n' + 'Tel: ' + citizen.owner.phone + '\n' + 'Mail: ' + citizen.owner.email + '\n' +
            #           #</br>
            #           'Bitte setze dich mit der Person in Verbindung, um genaueres wie Einsatzzeitraum und Bezahlung zu klären. \n' +
            #           #</br>
            #           'Vielen Dank und Viele Grüße \n'
            #           #</br>
            #           'Dein Abernten-Team \n',
            #           'no-reply@abernten.de',
            #           [company.owner.email]
            #         )

            messages.success(request, 'Die Kontaktdaten werden an den Interessenten versendet!',extra_tags='alert-success')
            return redirect('/interests')
        else:
            return redirect('/')

class DeclineInterestView(View):

    def get(self, request, id):
        if request.user.groups.filter(name__in=['Betrieb']).exists():
            # Company
            interested = InterestOffer.objects.get(pk=id)
            interested.state = 2
            interested.save()

            send_mail('Ablehnung ihres Hilfeangebotes für: ' + interested.task.title,
                      'Hallo ' + citizen.owner.first_name + ' ' +  citizen.owner.last_name + '. \n' +
                      'Vielen Dank, dass du Abernten.de nutzt! \n' +
                      #</br>
                      'Dein Hilfeangebot vom ' + interested.created_at + ' wurde leider abgelehnt. \n' +
                      'Dies kann viele verschiedene Gründe haben. Du kannst dich gerne auf ein anderes Hilfegesuch in deiner Nähe melden. \n'
                      #</br>
                      'Vielen Dank und Viele Grüße \n'
                      #</br>
                      'Dein Abernten-Team \n',
                      'no-reply@abernten.de',
                      [citizen.owner.email]
                    )

            messages.success(request, 'Die Kontaktdaten werden an den Interessenten versendet!',extra_tags='alert-success')
            return redirect('/interests')
        else:
            return redirect('/')

