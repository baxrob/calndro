import json

from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model, login, logout
#from django.contrib.auth import get_user_model, logout

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated

from schedul.models import Event, TimeSpan, EmailToken, DispatchLogEntry
from schedul.serializers import (
    EventSerializer, EventNotifySerializer,
    DispatchLogEntrySerializer, DispatchLogSerializer
)
from schedul.permissions import IsEventPartyOrAdmin
from schedul import services

from django.core.mail import send_mail

User = get_user_model()

from datetime import datetime
from django.utils import timezone
#from zoneinfo import ZoneInfo
def token_login(request, event):
    key = request.GET.get('et')
    #import ipdb; ipdb.set_trace()
    try:
        et = EmailToken.objects.get(pk=key)
        now = timezone.now()
        # X: custom err on expired ?
        if request.user != et.user and et.event == event and now < et.expires:
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

class EventList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Event.objects.all()
        else:
            return user.event_set.all()

    def get(self, request, format=None):
        events = self.get_queryset()
        serializer = EventSerializer(events, many=True,
            context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data,
            context={'request': request})
        if serializer.is_valid():
            event = serializer.save()
            enlog(event, request.user.email, 'UPDATE', 
                serializer.data['slots'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


#class EventDetail(GenericAPIView):
class EventDetail(APIView):
    
    permission_classes = [IsEventPartyOrAdmin]
    #serializer_class = EventSerializer
    #queryset = Event.objects

    token = None

    def get_object(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        self.token = services.token_login(self.request, event)
        self.check_object_permissions(self.request, event)
        if self.token:
            #print('logout', self.token.key)
            print('logout', self.token.key, self.token.user)
            logout(self.request)
        return event

    def get(self, request, pk, format=None):
        event = self.get_object()
        serializer = EventSerializer(event, context={'request': request})
        data = {"token": self.token.key} if self.token else {}
        user = self.token.user if self.token else request.user
        enlog(event, user.email, 'VIEW', serializer.data['slots'], data=data)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        event = self.get_object()

        serializer = EventSerializer(event, data=request.data, partial=True,
            context={'request': request})

        if serializer.is_valid():
            #event = serializer.save(prior_slots=event.slots.all())
            event = serializer.save()
            data = {"token": self.token.key} if self.token else {}
            user = self.token.user if self.token else request.user
            enlog(event, user.email, 'UPDATE', serializer.data['slots'], data)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        # X: admin only ?
        event = get_object_or_404(Event, pk=pk)
        self.check_object_permissions(request, event)
        if request.user.is_staff:
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
        {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')},
            status=status.HTTP_403_FORBIDDEN)


from django.core.mail import send_mail
def notify(event, sender, recip_email, url_base):
    recipient = User.objects.get(email=recip_email)
    token = EmailToken.objects.create(event=event, user=recipient)
    url = '%s%d/?et=%s' % (url_base, event.id, token.key)
    print(url, recip_email, sender)


#class EventNotify(GenericAPIView):
class EventNotify(APIView):
    permission_classes = [IsEventPartyOrAdmin]
    serializer_class = EventSerializer

    def post(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        token = services.token_login(self.request, event)

        self.check_object_permissions(self.request, event)

        user = request.user

        if token:
            print('logout', token.key, user)
            logout(request)
        
        event.sender = user
        serializer = EventNotifySerializer(event, data=request.data,
            context={'request': request})
        
        if serializer.is_valid():

            for recip_email in serializer.validated_data['parties']:

                # X: just pass request for user/url
                u = request._request.build_absolute_uri('/')
                #notify(event, request.user, umail['email'], u)
                #notify(event, request.user.email, recip_email, u)
                notify(event, user.email, recip_email, u)

                #services.notify(event, user.email, recip_email)

            effector = event.sender#request.user
            #effector = token.user

            log_data = {"token": token.key} if token else {}
            # X:
            log_data['recipients'] = serializer.validated_data['parties']
            enlog(event, effector, 'NOTIFY', serializer.data['slots'],
                log_data)

            return Response(serializer.data,
                status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class DispatchLog(APIView):
    permission_classes = [IsEventPartyOrAdmin]

    def get(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, event)
        logs = event.dispatch_log.all()
        serializer = DispatchLogSerializer({'event': event, 'entries': logs,
            'parties': event.parties},
            context={'request': request})
        #import ipdb; ipdb.set_trace()
        return Response(serializer.data)
         

