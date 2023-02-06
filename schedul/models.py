import os
import binascii

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

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

class Event(models.Model):
    title = models.CharField(max_length=256, default=nym_gen)
    parties = models.ManyToManyField(User)

    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk': self.pk})


class TimeSpan(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
        related_name='slots')
    begin = models.DateTimeField()
    duration = models.DurationField()

    class Meta:
        ordering = ['begin']
        

class EmailToken(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=40, primary_key=True, editable=False)
    expires = models.DateTimeField(editable=False)

    def clean(self, *args, **kwargs):
        if self.user not in self.event.parties.all():
            raise ValidationError({'user': 'User must be event party'})

    def save(self, *args, **kwargs):
        if not self.expires:
            self.expires = timezone.now() + timedelta(
                days=settings.EMAILTOKEN_EXPIRATION_DAYS)
        if not self.key:
            self.key = binascii.hexlify(os.urandom(20)).decode()
        self.full_clean()
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

    # Maximum email length per RFC 5321
    effector = models.CharField(max_length=254)

    # Up to 30 64-char timespan records in json array
    slots = models.CharField(max_length=2048)

    # Maximum length for {"token":...,"recipient":"..."}
    data = models.CharField(max_length=512, default='{}')

