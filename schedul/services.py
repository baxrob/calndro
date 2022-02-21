from datetime import datetime
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.core.mail import send_mail

from rest_framework.exceptions import ValidationError

from schedul.models import EmailToken
from schedul.serializers import DispatchLogEntrySerializer


User = get_user_model()


def notify(event, sender_email, recip_email):
    recipient = User.objects.get(email=recip_email)
    token = EmailToken.objects.create(event=event, user=recipient)
    url_base = event.get_absolute_url()
    url = '%s?et=%s' % (url_base, token.key)
    msg = 'expires %s' % token.expires
    message = '%s\n%s' %(url, msg)
    subject = "%s'%s' updated" % (settings.EMAIL_SUBJECT_PREFIX,
        event.title)
    from_email = sender_email
    recipient_list = [recip_email]
    #print('ff', from_email)
    #print('PRESEND', message)
    #return
    send_mail(subject, message, from_email, recipient_list) 

def token_login(request, event):
    key = request.GET.get('et')
    try:
        et = EmailToken.objects.get(pk=key)
        now = timezone.now()
        # X: custom err on expired ?
        if request.user != et.user and et.event == event:# and now < et.expires:
            if now >= et.expires:
                raise ValidationError(['Token Expired'])
            login(request, et.user) 
            return et
        else:
            return None
    except EmailToken.DoesNotExist:
        return None
    

def enlog(event, effector, occurrence, slots, data={}):
    serializer = DispatchLogEntrySerializer(data={'event': event,
        'effector': effector, 'occurrence': occurrence, 'slots': slots,
        'data': data})
    if serializer.is_valid():
        entry = serializer.save()
        return serializer.data
    else:
        return serializer.errors
