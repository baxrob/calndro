import os
import binascii

from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

def nym_gen(n=5):
    import random
    v = random.sample(list('aeiouy'), 6)
    c = random.sample(list('bcdfghjklmnpqrstvwxz'), 20)
    s = c if random.randint(0, 1) else v
    r = ''
    for i in range(n):
        r += s.pop()
        s = c if s == v else v
    return r


'''
class EventManager(models.Manager):
    def foo(self):
        import ipdb; ipdb.set_trace()
        pass
    
    def create(self, *args, **kwargs):
        import ipdb; ipdb.set_trace()
        event = super().create(*args, **kwargs)
        return event
'''


class Event(models.Model):
    title = models.CharField(max_length=256, default=nym_gen)
    parties = models.ManyToManyField(User)
    #initiator = models.ForeignKey(get_user_model())
    #initiated = models.DateTimeField()

    #objects = models.Manager()
    #objects = EventManager()

    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk})



class TimeSpan(models.Model):
    event = models.ForeignKey( Event, on_delete=models.CASCADE,
        related_name='slots')
    begin = models.DateTimeField()
    duration = models.DurationField()

    class Meta:
        ordering = ['begin']


def five_days_hence():
    return timezone.now() + timedelta(days=5)

class EmailToken(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=40, primary_key=True, editable=False)
    expires = models.DateTimeField(default=five_days_hence,
        editable=False)
    #expires = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = binascii.hexlify(os.urandom(20)).decode()
        #if not self.expires:
        #    self.expires = timezone.now() + timedelta(days=5)
        return super().save(*args, **kwargs)


class DispatchOccurrenceChoices(models.TextChoices):
    UPDATE = 'UPDATE', 'Update'
    NOTIFY = 'NOTIFY', 'Notify'
    VIEW = 'VIEW', 'View'


class DispatchLogEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
        related_name='dispatch_log')
    when = models.DateTimeField(auto_now_add=True)
    occurrence = models.CharField(max_length=32,
        choices=DispatchOccurrenceChoices.choices)
    #effector = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    effector = models.CharField(max_length=128)
    #effector = models.EmailField()

    slots = models.CharField(max_length=1024)
    data = models.CharField(max_length=128, default='{}')

