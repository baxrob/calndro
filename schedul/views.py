import json

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from schedul.models import Event, TimeSpan, DispatchLogEntry
from schedul.serializers import EventSerializer, TimeSpanSerializer, DispatchLogEntrySerializer, DispatchLogSerializer

from .permissions import IsEventPartyOrAdmin

from django.core.mail import send_mail


#def notify(party, event, *args, **kwargs):
def notify(*args, **kwargs):
    print('notify:', args, kwargs)
    pass 

def enlog(event, effector, occurrence, slots, data={}):
    entry = DispatchLogEntry.objects.create(event=event, effector=effector,
        occurrence=occurrence, slots=slots, data=data)
    return entry

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
        token = request.GET.get('ntok')
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
            serializer.save()
            entry = DispatchLogEntry.objects.create(**{
                'event': serializer.instance,
                'effector': request.user.email,
                'occurrence': 'UPDATE',
                'slots': json.dumps(serializer.initial_data['slots'])
            })
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

    def get_object(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, event)
        return event

    def get(self, request, pk, format=None):
        #import ipdb; ipdb.set_trace()
        # X: ? this interferes with ui checking delete/option availability
        #   no, self.check_object... does -- via browserviewclassfoo
        event = get_object_or_404(Event, pk=pk)
        foo = self.check_object_permissions(request, event)
        #print('?check_o_perm return', foo)
        
        event = self.get_object()
        serializer = EventSerializer(event, context={'request': request})
        token = request.GET.get('ntok')
        data = {'token': token}# if token else {}
        enlog(event, request.user.email, 'VIEW', 
            #event.slots.all(), data=data)
            json.dumps(serializer.data['slots']), data=data)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        #self.check_object_permissions(request, event)

        event = self.get_object()

        #serializer = EventSerializer(event, data=request.data, exclude=['parties'], #partial=True,
        serializer = EventSerializer(event, data=request.data, partial=True,
            context={'request': request})
        if serializer.is_valid():
            serializer.save()
            #import ipdb; ipdb.set_trace()
            # X: ignore unchanged - in serializer or here ?
            entry = DispatchLogEntry.objects.create(**{
                'event': serializer.instance,
                'effector': request.user.email,
                'occurrence': 'UPDATE',
                'slots': json.dumps(serializer.initial_data['slots'])
            })
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            # ? return Response(serializer.validated_data)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        #self.check_object_permissions(request, event)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#class EventNotify(GenericAPIView):
class EventNotify(APIView):
    permission_classes = [IsEventPartyOrAdmin]
    serializer_class = EventSerializer

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
        serializer = EventSerializer(event, data=request.data, partial=True,
            context={'request': request})
        #import ipdb; ipdb.set_trace()
        # X: rather, full serializer .. so some of this is cruft
        if serializer.is_valid():
            if not 'parties' in serializer.validated_data:
                return Response({'parties': 'required'},
                    status=status.HTTP_400_BAD_REQUEST)
            for umail in serializer.validated_data['parties']:
                # X: test parties in event ..
                notify(umail['email'], pk)
                effector = umail['email']
                enlog(event, effector, 'NOTIFY', 
                    json.dumps(serializer.data['slots']))
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
        serializer = DispatchLogSerializer({'event': event, 'entries': logs},
        #serializer = DispatchLogEntrySerializer(logs, many=True,
            context={'request': request})
        #import ipdb; ipdb.set_trace()
        return Response(serializer.data)
         

