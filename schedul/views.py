import json

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model, login

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

def token_login(request, event):
    key = request.GET.get('et')
    try:
        # X: logged in as non-key user case
        et = EmailToken.objects.get(pk=key)
        if et.event is event:
            login(request, et.user) 
            return key
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
        token = request.GET.get('et')
        if token:
            pass
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

        self.token_key = token_login(self.request, event)

        self.check_object_permissions(self.request, event)
        return event

    def get(self, request, pk, format=None):
        #import ipdb; ipdb.set_trace()
        event = self.get_object()
        serializer = EventSerializer(event, context={'request': request})

        #token = request.GET.get('et')
        #data = {"token": token} if token else {}
        data = {"token": token} if self.token_key else {}
        
        # X: temp dbg hack
        if True or not request.user.is_staff:
            enlog(event, request.user.email, 'VIEW', serializer.data['slots'],
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
            # X: ignore unchanged - in serializer or here ?
            #entry = DispatchLogEntry.objects.create(**{
            #    'event': serializer.instance,
            #    'effector': request.user.email,
            #    'occurrence': 'UPDATE',
            #    # X: initial data or ?? or re-serialize saved ?
            #    #    validated_data
            #    'slots': json.dumps(serializer.initial_data['slots'])
            #    # X: not serializable
            #    #'slots': json.dumps(serializer.validated_data['slots'])
            #    #'slots': serializer.validated_data['slots']
            #})
            #esrz = DispatchLogEntrySerializer(data={
            #    'event': serializer.instance,
            #    'effector': request.user.email,
            #    'occurrence': 'UPDATE',
            #    # X: initial data or ?? or re-serialize saved ?
            #    #    validated_data
            #    #'slots': json.dumps(serializer.initial_data['slots']),
            #    # X: not serializable
            #    #'slots': json.dumps(serializer.validated_data['slots'])
            #    'slots': serializer.data['slots'],
            #    #'slots': serializer.validated_data['slots'],
            #    'data': {}
            #})
            #if esrz.is_valid():
            #    entry = esrz.save()
            #    print(entry)
            data = {"token": token} if self.token_key else {}
            enlog(event, request.user.email, 'UPDATE', 
                serializer.data['slots'], data)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        #self.check_object_permissions(request, event)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def notify(event, sender, recip_email):
    recipient = User.objects.get(email=recip_email)
    token = EmailToken.objects.create(event=event, user=recipient)
    url = 'http://192.168.1.128:9000/%d/?et=%s' % (event.id, token.key)
    print(url)


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


#class EventNotify(GenericAPIView):
class EventNotify(APIView):
    permission_classes = [IsEventPartyOrAdmin]
    serializer_class = EventSerializer

    # X: kill this - presume /id/ get
    def get(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        self.check_object_permissions(self.request, event)
        serializer = EventSerializer(event, context={'request': request})
        #import ipdb; ipdb.set_trace()
        return Response({
            'parties': serializer.data['parties'],
            'slots': serializer.data['slots']
        })

    def post(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)

        token_key = token_login(self.request, event)

        self.check_object_permissions(self.request, event)
        
        event.sender = request.user
        serializer = EventNotifySerializer(event, data=request.data,
            context={'request': request})
        
        #import ipdb; ipdb.set_trace()
        if serializer.is_valid():

            for umail in serializer.validated_data['parties']:
                # X: test parties in event ..

                notify(event, request.user, umail['email'])

                effector = request.user

                log_data = {"token": token} if token_key else {}
                enlog(event, effector, 'NOTIFY', serializer.data['slots'],
                    log_data)

            return Response(serializer.data,
                status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


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
         

