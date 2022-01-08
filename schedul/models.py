from django.db import models
from django.conf import settings


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
    #initiator
    #initiated = models.DateTimeField()


class TimeSpan(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, 
        related_name='span')
    begin = models.DateTimeField()
    duration = models.DurationField()

    class Meta:
        ordering = ['begin']

'''
class Dispatch(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

class LogItem(models.Model):
    dispatch = models.ForeignKey(Dispatch, on_delete=models.CASCADE)
    occurence
    when
    detail

    @property
    def status(self):
        # or choice class?
        pass
'''
