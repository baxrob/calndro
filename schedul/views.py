from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from schedul.models import Event, TimeSpan
from schedul.serializers import EventSerializer, TimeSpanSerializer

from .permissions import IsEventParty

class EventList(GenericAPIView):

    permission_classes = [IsEventParty, IsAuthenticated]
    #permission_classes = [IsEventParty]
    serializer_class = EventSerializer
    queryset = Event.objects

    def get(self, request, format=None):
        #events = Event.objects.all()
        #import ipdb; ipdb.set_trace()
        #if request.user.isI
        events = request.user.event_set.all()
        serializer = EventSerializer(events, many=True) 
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data)
        #import ipdb; ipdb.set_trace()
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

class EventDetail(GenericAPIView):
#class EventDetail(APIView):
    
    permission_classes = [IsEventParty]
    serializer_class = EventSerializer
    queryset = Event.objects

    def get(self, request, pk, format=None):
        #import ipdb; ipdb.set_trace()
        # X: ? this interferes with ui checking delete/option availability
        #   no, self.check_object... does
        event = get_object_or_404(Event, pk=pk)
        
        serializer = EventSerializer(event)
        self.check_object_permissions(request, event)
        return Response(serializer.data)
        '''
        try:
            event = Event.objects.get(pk=pk)
            self.check_object_permissions(request, event)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response({'Detail': 'Not found'},
                status=status.HTTP_404_NOT_FOUND)
        '''

    def patch(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        #self.check_object_permissions(request, event)

        serializer = EventSerializer(event, data=request.data, partial=True)
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
