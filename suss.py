#!/bin/env python

import ipdb
#import importlib
from django.test import TestCase

#from rest_framework.authtoken.models import Token
from rest_framework.test import (
    APIRequestFactory, APITestCase, 
    APILiveServerTestCase, URLPatternsTestCase,
    force_authenticate,
    RequestsClient
)

class RequestCase(APITestCase):
    pass


#import sys
#from django.core.management import execute_from_command_line
#execute_from_command_line(sys.argv)
import django
django.setup()

from schedul.views import EventList, EventDetail

import os
print(os.getcwd())


## serializer render parse
print('serializer render parse')

import io

from schedul.models import *
from schedul.serializers import *
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

ipdb.set_trace()

e = Event.objects.get(pk=7)
es = EventSerializer(e)
esc = JSONRenderer().render(es.data)
escs = io.BytesIO(esc)
escsd = JSONParser().parse(escs)
escsds = EventSerializer(data=escsd)
print(e, es, esc, escs, escsd, escsds)
escsds.is_valid()
escsds.save()

t4 = TimeSpan.objects.get(pk=4)
t4s = TimeSpanSerializer(t4)
t4sc = JSONRenderer().render(t4s.data)
t4scs = io.BytesIO(t4sc)
t4scsd = JSONParser().parse(t4scs)

escs2 = io.BytesIO(esc)
escsd2 = JSONParser().parse(escs2)
escsd2['span'][2] = t4scsd

ipdb.set_trace()



#
print('request factory / response')
ipdb.set_trace()

factory = APIRequestFactory()

request = factory.get('/')
print(request.body)
response = EventList.as_view()(request)
response.render()
print(response.content)

request = factory.post('/', {'parties': [{'email': 'zo@localhost'}], 'span': [ { "begin": "2021-12-24T22:58:26.611Z", "duration": "02:30:00" } ]}, format='json')
print(request.body)
response = EventList.as_view()(request)
response.render()
print(response.content)

ipdb.set_trace()

# multipart fails on missing fields, why?
request = factory.post('/', {'parties': [ {'email': 'zo@localhost'} ], 'span': [ { "begin": "2021-12-24T22:58:26.611Z", "duration": "02:30:00" } ]})
print(request.body)
response = EventList.as_view()(request)
response.render()
print(response.content)

request = factory.get('/')
print(request.body)
response = EventList.as_view()(request)
response.render()
print(response.content)

request = factory.get('/1/')
print(request.body)
response = EventDetail.as_view()(request, pk=1)
response.render()
print(response.content)

request = factory.patch('/1', {'span': []}, format='json')
print(request.body)
response = EventDetail.as_view()(request, pk=1)
response.render()
print(response.content)

request = factory.get('/1')
print(request.body)
response = EventDetail.as_view()(request, pk=1)
response.render()
print(response.content)

request = factory.get('/100/')
print(request.body)
response = EventDetail.as_view()(request, pk=100)
response.render()
print(response.content)


## view /url

ipdb.set_trace()


## schematum

# from manage generateschema



## fixtures




## authn/z



## env/s



## logging / testabil



## email / reference / loop/s



## q / m / t





