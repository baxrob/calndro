from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from schedul.models import Event, TimeSpan
from schedul.serializers import EventSerializer, TimeSpanSerializer

from .permissions import IsEventPartyOrAdmin

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
        events = self.get_queryset()
        serializer = EventSerializer(events, many=True,
            context={'request': request}) 
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data,
            context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


#class EventDetail(GenericAPIView):
class EventDetail(APIView):
    
    permission_classes = [IsEventPartyOrAdmin]
    #permission_classes = [IsEventParty|IsAdminUser]
    serializer_class = EventSerializer
    queryset = Event.objects

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
        print(foo)
        
        #event =
        self.get_object()
        serializer = EventSerializer(event, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        #self.check_object_permissions(request, event)

        serializer = EventSerializer(event, data=request.data, partial=True,
            context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        #self.check_object_permissions(request, event)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DispatchList(APIView):
    
    def get(self):
        pass


class DispatchDetail(APIView):
    
    def get(self):
        pass


class DispatchNotification(APIView):
    
    def post(self):
        pass
