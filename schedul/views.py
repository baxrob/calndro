import json

from django.shortcuts import get_object_or_404
from django.conf import settings

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


class EventList(APIView):
    permission_classes = [IsAuthenticated]

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
            services.enlog(event, request.user.email, 'UPDATE', 
                serializer.data['slots'], {'opened': 'created'})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class EventDetail(APIView):
    permission_classes = [IsEventPartyOrAdmin]

    token = None

    def get_object(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        self.token = services.token_login(self.request, event)
        self.check_object_permissions(self.request, event)
        return event

    def get(self, request, pk, format=None):
        event = self.get_object()
        serializer = EventSerializer(event, context={'request': request})
        data = {"token": self.token.key} if self.token else {}
        user = self.token.user if self.token else request.user
        services.enlog(event, user.email, 'VIEW', serializer.data['slots'],
            data=data)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        event = self.get_object()

        serializer = EventSerializer(event, data=request.data, partial=True,
            context={'request': request})

        if serializer.is_valid():
            event = serializer.save()
            data = {"token": self.token.key} if self.token else {}
            user = self.token.user if self.token else request.user
            services.enlog(event, user.email, 'UPDATE',
                serializer.data['slots'], data)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        event = self.get_object()
        self.check_object_permissions(request, event)
        serializer = EventSerializer(event, context={'request': request})
        services.enlog(event, request.user.email, 'UPDATE', 
            serializer.data['slots'], {'closed': 'deleted'})
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventNotify(APIView):
    permission_classes = [IsEventPartyOrAdmin]

    def post(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=pk)
        token = services.token_login(self.request, event)
        self.check_object_permissions(self.request, event)

        # X: 
        #event.sender = request.user
        serializer = EventNotifySerializer(event, data=request.data,
            context={'request': request})
        
        if serializer.is_valid():
            data = serializer.validated_data

            if 'sender' in data:
                event.sender = {'email': data['sender']}
            elif request.user.is_active:
                event.sender = request.user
            else:
                event.sender = {'email': settings.DEFAULT_FROM_EMAIL}

            sender_email = (data['sender'] if 'sender' in data else
                request.user.email if request.user.is_active else
                settings.DEFAULT_FROM_EMAIL)

            scheme = request.META['wsgi.url_scheme']
            # X: remove setting
            domain = settings.HOST_DOMAIN 
            domain = request.META['SERVER_NAME'] 
            url = "%s://%s" % (scheme, domain)
            port = request.META['SERVER_PORT']
            if port:
                url = "%s:%s" % (url, port)
            is_invite = data['invitation'] if 'invitation' in data else False

            for recip_email in serializer.validated_data['parties']:

                services.notify(event, sender_email, recip_email, 
                    url, is_invite)
                log_data = {"token": token.key} if token else {}
                log_data['recipient'] = recip_email
                log_data['sender'] = sender_email
                services.enlog(event, request.user.email, 'NOTIFY',
                    serializer.data['slots'], log_data)
            
            return Response(serializer.data,
                status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class DispatchLog(APIView):
    permission_classes = [IsEventPartyOrAdmin]

    def get(self, request, pk, format=None):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        token = services.token_login(self.request, event)
        self.check_object_permissions(self.request, event)
        logs = event.dispatch_log.all()
        serializer = DispatchLogSerializer({'event': event, 'entries': logs,
            'parties': event.parties}, context={'request': request})
        return Response(serializer.data)
         

