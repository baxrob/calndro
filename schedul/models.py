from django.db import models
from django.conf import settings


class Event(models.Model):
    parties = models.ManyToManyField(settings.AUTH_USER_MODEL)


class TimeSpan(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, 
        related_name='span')
    begin = models.DateTimeField()
    duration = models.DurationField()

    class Meta:
        ordering = ['begin']
