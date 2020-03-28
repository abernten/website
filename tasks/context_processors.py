from .models import TaskOffer
from datetime import datetime

def task_offer_count(request):
    if request.user.is_anonymous:
        return {}

    return {
        'task_offer_count': TaskOffer.objects.filter(task__company__owner__id=request.user.id, state=0, task__done=False, task__end_date__gt=datetime.now()).count()
    }
