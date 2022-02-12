import json

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model, login, logout

from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from schedul.models import Event, TimeSpan, EmailToken, DispatchLogEntry
from schedul.serializers import (
    EventSerializer, EventNotifySerializer,
    #EventUpdateSerializer, TimeSpanSerializer,
    DispatchLogEntrySerializer, DispatchLogSerializer
)

from schedul.permissions import IsEventPartyOrAdmin

from django.core.mail import send_mail

User = get_user_model()

from datetime import datetime
from django.utils import timezone
from zoneinfo import ZoneInfo
def token_login(request, event):
    key = request.GET.get('et')
    try:
        # X: logged in as non-key user case
        et = EmailToken.objects.get(pk=key)
        #import ipdb; ipdb.set_trace()
        now = datetime.now(ZoneInfo('UTC'))
        now = timezone.now()
        if et.event == event and now < et.expires:
            login(request, et.user) 
            return et
        else:
            return None
    except EmailToken.DoesNotExist:
        return None
    

def enlog(event, effector, occurrence, slots, data={}):
    #entry = DispatchLogEntry.objects.create(event=event, effector=effector,
    #    occurrence=occurrence, slots=slots, data=data)
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
    #permission_classes = [IsEventParty, IsAuthenticated]
    #permission_classes = [IsEventParty]
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get_queryset(self):
        #import ipdb; ipdb.set_trace()
        user = self.request.user
        if user.is_staff:
            return Event.objects.all()
        else:
            return user.event_set.all()

    def get(self, request, format=None):
        #events = Event.objects.all()
        #import ipdb; ipdb.set_trace()
        #if request.user.isI
        '''
        if request.user.is_superuser:
            events = Event.objects.all()
        else:
            events = request.user.event_set.all()
        '''
        #import ipdb; ipdb.set_trace()
        #token = request.GET.get('et')
        #if token:
        #    pass
            #pk = 
            #return HttpResponseRedirect(reverse('event-detail', args=[pk], request=request))
        events = self.get_queryset()
        serializer = EventSerializer(events, many=True,
            context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data,
            context={'request': request})
        if serializer.is_valid():
            event = serializer.save()
            #entry = DispatchLogEntry.objects.create(**{
            #    'event': serializer.instance,
            #    'effector': request.user.email,
            #    'occurrence': 'UPDATE',
            #    'slots': json.dumps(serializer.initial_data['slots'])
            #})
            enlog(event, request.user.email, 'UPDATE', 
                serializer.data['slots'])
            #import ipdb; ipdb.set_trace()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            #return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


#class EventDetail(GenericAPIView):
class EventDetail(APIView):
    
    permission_classes = [IsEventPartyOrAdmin]
    #permission_classes = [IsEventParty|IsAdminUser]
    #serializer_class = EventSerializer
    #queryset = Event.objects

    token_key = None

    def get_object(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        #import ipdb; ipdb.set_trace()

        self.token = token_login(self.request, event)
        #import ipdb; ipdb.set_trace()
         
        self.check_object_permissions(self.request, event)

        if self.token:
            print('logout', self.token.key)
            logout(self.request)

        return event

    def get(self, request, pk, format=None):
        #req_user = request.user
        #import ipdb; ipdb.set_trace()
        event = self.get_object()
        serializer = EventSerializer(event, context={'request': request})

        #token = request.GET.get('et')
        #data = {"token": token} if token else {}
        data = {"token": self.token.key} if self.token else {}
        
        # X: temp dbg hack
        if True or not request.user.is_staff:
            #enlog(event, request.user.email, 'VIEW', serializer.data['slots'],
            effector = self.token.user.email if self.token else request.user.email
            enlog(event, effector, 'VIEW', serializer.data['slots'],
                data=data)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        event = self.get_object()

        #serializer = EventSerializer(event, data=request.data, exclude=['parties'], #partial=True,
        #serializer = EventUpdateSerializer(event, data=request.data,
        #    context={'request': request})

        serializer = EventSerializer(event, data=request.data, partial=True,
            context={'request': request})
        #serializer = EventUpdateSerializer(event, data=request.data, #partial=True,
        #    context={'request': request})

        #import ipdb; ipdb.set_trace()
        if serializer.is_valid():
            event = serializer.save(prior_slots=event.slots.all())
            data = {"token": self.token_key} if self.token_key else {}
            effector = self.token.user.email if self.token else request.user.email
            enlog(event, effector, 'UPDATE', 
                serializer.data['slots'], data)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        #self.check_object_permissions(request, event)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from django.core.mail import send_mail
def notify(event, sender, recip_email, url_base):
    recipient = User.objects.get(email=recip_email)
    token = EmailToken.objects.create(event=event, user=recipient)
    url = '%s%d/?et=%s' % (url_base, event.id, token.key)
    print(url)


'''
#def notify(party, event, *args, **kwargs):
def _notify(party, event):
    print('notify:', party, event)
    import ipdb; ipdb.set_trace()
    user = User.objects.get(email=party)
    token = EmailToken(event=event, user=user)
    print(vars(token))
    token = EmailToken(event, user)
    print(vars(token))
    token = EmailToken(event.id, user.id)
    print(vars(token))
    token = EmailToken.objects.create(event=event, user=user)#event.id, user.id)
    print(vars(token))
    #token.save()
    #print(token)
'''


#class EventNotify(GenericAPIView):
class EventNotify(APIView):
    permission_classes = [IsEventPartyOrAdmin]
    serializer_class = EventSerializer

    # X: kill this - presume /id/ get
    #    or response no_content
    '''
    def get(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        self.check_object_permissions(self.request, event)
        serializer = EventSerializer(event, context={'request': request})
        #import ipdb; ipdb.set_trace()
        return Response({
            'parties': serializer.data['parties'],
            'slots': serializer.data['slots']
        })
    '''

    def post(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)

        token = token_login(self.request, event)

        self.check_object_permissions(self.request, event)

        event.sender = request.user

        if token:
            logout(request)
        
        serializer = EventNotifySerializer(event, data=request.data,
            context={'request': request})
        
        #import ipdb; ipdb.set_trace()
        if serializer.is_valid():

            for umail in serializer.validated_data['parties']:

                # X: just pass request for user/url
                u = request._request.build_absolute_uri('/')
                notify(event, request.user, umail['email'], u)

            effector = event.sender#request.user
                #effector = token.user

            log_data = {"token": token.key} if token else {}
            # X:
            log_data['recipients'] = serializer.validated_data['parties'] #umail['email']
            enlog(event, effector, 'NOTIFY', serializer.data['slots'],
                log_data)

            return Response(serializer.data,
                status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


        '''
        #serializer = EventNotifySerializer(event, data=request.data,
        #    context={'request': request})
        serializer = EventSerializer(event, data=request.data, partial=True,
            context={'request': request})
        #import ipdb; ipdb.set_trace()
        # X: rather, full serializer .. so some of this is cruft
        if serializer.is_valid():
            if not 'parties' in serializer.validated_data:
                return Response({'parties': 'required'},
                    status=status.HTTP_400_BAD_REQUEST)
            for evt_party in event.parties:
                import ipdb; ipdb.set_trace()
            for umail in serializer.validated_data['parties']:
                # X: test parties in event ..
                notify(umail['email'], pk)
                effector = umail['email']
                enlog(event, effector, 'NOTIFY', serializer.data['slots'])
            return Response(serializer.validated_data,
                status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)
        '''
        

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
         

