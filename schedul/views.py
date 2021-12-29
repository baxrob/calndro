from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from schedul.models import Event, TimeSpan
from schedul.serializers import EventSerializer, TimeSpanSerializer

class EventList(APIView):

    def get(self, request, format=None):
        events = Event.objects.all()
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

class EventDetail(APIView):
    
    def get(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
