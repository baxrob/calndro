from django.contrib.auth import get_user_model
from rest_framework import serializers

from schedul.models import Event, TimeSpan, DispatchLogEntry
#from .models import Dispatch, LogItem


User = get_user_model()

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()


class TimeSpanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TimeSpan
        fields = ['begin', 'duration']


#class EventSerializer(serializers.ModelSerializer):
class EventSerializer(serializers.HyperlinkedModelSerializer):
    parties = UserSerializer(many=True)
    slots = TimeSpanSerializer(many=True)
    log_url = serializers.HyperlinkedIdentityField(
        view_name='dispatch-log')
    notify = serializers.HyperlinkedIdentityField(view_name='event-notify')
    #list_url = serializers.HyperlinkedIdentityField(view_name='event-list')

    class Meta:
        model = Event
        fields = ['id', 'url', 'log_url', 'title', 'parties', 'slots', 'notify']#,
            #'list_url']
        #read_only_fields = ['parties']
        #read_only_fields = ['title']

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop('exclude') if 'exclude' in kwargs else []
        #import ipdb; ipdb.set_trace()
        super().__init__(*args, **kwargs)
        for field_name in set(self.fields):
            if field_name in exclude:
                self.fields.pop(field_name) 
            #print(field)

    def validate_slots(self, value):
        #print('SLOTS:', value)
        #print('super:', super)
        return value
    def validate_parties(self, value):
        #print('PARTIES:', value)
        return value

    def validate(*args, **kwargs):
        #print('ARGS', args[0], 'DATA', args[1], 'KWARGS', kwargs)
        #pass
        #import ipdb; ipdb.set_trace()
        return args[1]
        return super().validate(*args, **kwargs)

    def create(self, validated_data):
        if 'title' in validated_data and len(validated_data['title']):
            event = Event.objects.create(title=validated_data['title'])
        else:
            event = Event.objects.create()
        for party in validated_data.get('parties'):
            # X: move to ?? ; must set is_active = False if new
            party_obj = User.objects.get_or_create(
                #username=party['email'], 
                email=party['email']
            )
            user = party_obj[0]
            if party_obj[1]:
                user.username = user.email
                user.is_active = False
                user.save()
            print('user', user, 'created', party_obj[1])

            #import ipdb; ipdb.set_trace()
            event.parties.add(user)
        for slot in validated_data.get('slots'):
            TimeSpan.objects.create(event=event, **slot)
        return event

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            instance.title = validated_data['title']
            instance.save()
        slots_remain = []
        #print(validated_data)
        #import ipdb; ipdb.set_trace()
        if 'slots' not in validated_data:
            raise serializers.ValidationError(
                {'slots': ['This field is required']})
        for slot in validated_data['slots']:
            try:
                found = instance.slots.get(**slot)
                slots_remain.append(found.id)
            #except Event.DoesNotExist:
            except TimeSpan.DoesNotExist:
                #import ipdb; ipdb.set_trace()
                slot['event_id'] = instance.id
                obj = TimeSpan.objects.create(**slot)
                instance.slots.add(obj)
                slots_remain.append(obj.id)
        for slot in instance.slots.all():
            if slot.id not in slots_remain:
                slot.delete()
        return instance
         

class EventUpdateSerializer(serializers.Serializer):
    slots = TimeSpanSerializer(many=True)

    def update(self, instance, validated_data):
        return instance


class EventNotifySerializer(serializers.Serializer):
    parties = UserSerializer(many=True)


class DispatchLogEntrySerializer(serializers.ModelSerializer):
    #when = serializers.DateTimeField()
    #occurrence = serializers.CharField()
    #effector = serializers.EmailField()
    #slots = serializers.JSONField()
    #data = serializers.JSONField()
    class Meta:
        model = DispatchLogEntry
        # X:
        fields = '__all__'
    def to_representation(self, instance):
        data = super().to_representation(instance)
        #import ipdb; ipdb.set_trace()
        # X: validate slots = instance.slots
        import json
        data['slots'] = json.loads(data['slots'])
        #data['data'] = json.loads(data['data'])
        return data

class DispatchLogSerializer(serializers.Serializer):
    #event = serializers.HyperlinkedIdentityField(view_name='event-detail')
    event = serializers.HyperlinkedRelatedField(read_only=True,
        view_name='event-detail')
    entries = DispatchLogEntrySerializer(many=True)


