from django.db import models

class InterestOffer(models.Model):
    class Meta:
        verbose_name        = 'Interessensangebot'
        verbose_name_plural = verbose_name + 'e'

    OPEN     = 0
    APPROVED = 1
    DECLINED = 2

    STATES = [
        (0, 'Offen'),
        (1, 'Bestätigt'),
        (2, 'Abgelehnt'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    # Status
    state = models.IntegerField(default=0, choices=STATES)

    # Referenzen
    task    = models.ForeignKey('tasks.Task', on_delete=models.CASCADE)
    citizen = models.ForeignKey('erntehelfer.CitizenProfile', on_delete=models.CASCADE)

    def __str__(self):
        return 'Angebot von "{} {}" an "{}"'.format(self.citizen.owner.first_name, self.citizen.owner.last_name, self.task.title)
