import os
import binascii

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


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


class Event(models.Model):
    title = models.CharField(max_length=256, default=nym_gen)
    parties = models.ManyToManyField(settings.AUTH_USER_MODEL)
    #initiator = models.ForeignKey(get_user_model())
    #initiated = models.DateTimeField()


class TimeSpan(models.Model):
    event = models.ForeignKey( Event, on_delete=models.CASCADE,
        related_name='slots')
    begin = models.DateTimeField()
    duration = models.DurationField()

    class Meta:
        ordering = ['begin']


#class DispatchEmailToken(models.Model):
class EmailToken(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE#, related_name='slots'
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    key = models.CharField(max_length=40, primary_key=True, editable=False)
    expires = models.DateTimeField(
        default=datetime.now(ZoneInfo('UTC')) + timedelta(days=5),
        editable=False)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = binascii.hexlify(os.urandom(20)).decode()
        return super().save(*args, **kwargs)

    '''
    @classmethod
    def generate_expiry(self):
        pass
    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()
    '''
    

class DispatchOccurrenceChoices(models.TextChoices):
    UPDATE = 'UPDATE', 'Update'
    NOTIFY = 'NOTIFY', 'Notify'
    VIEW = 'VIEW', 'View'

class DispatchLogEntry(models.Model):
    # X: 
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
        related_name='dispatch_log')
    when = models.DateTimeField(auto_now_add=True)
    occurrence = models.CharField(max_length=32,
        choices=DispatchOccurrenceChoices.choices)
    #effector = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    effector = models.CharField(max_length=128)
    #effector = models.EmailField()

    #occurence = models.CharField(max_length=32)
    #when = models.CharField(max_length=32)
    slots = models.CharField(max_length=1024)
    #parties = models.CharField(max_length=4096)
    data = models.CharField(max_length=128, default='{}')

