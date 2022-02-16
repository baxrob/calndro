import json
from django.contrib.auth import get_user_model
from rest_framework import serializers

from schedul.models import Event, TimeSpan, DispatchLogEntry


User = get_user_model()


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data['email']

    def to_internal_value(self, data):
        #print('TIV', data)
        dd = super().to_internal_value(dict(email=data))
        #import ipdb; ipdb.set_trace()
        return dd['email']
        #return data['email']
        return data
        #return dict(email=data)


class TimeSpanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TimeSpan
        fields = ['begin', 'duration']


class EventSerializer(serializers.HyperlinkedModelSerializer):
    parties = UserSerializer(many=True)
    slots = TimeSpanSerializer(many=True)
    log_url = serializers.HyperlinkedIdentityField(
        view_name='dispatch-log')
    notify_url = serializers.HyperlinkedIdentityField(
        view_name='event-notify')

    # X: ???
    list_url = serializers.HyperlinkedRelatedField(view_name='event-list',
        read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'url', 'log_url', 'title', 'parties', 'slots', 
            'notify_url', 'list_url']
        read_only_fields = ['parties']

    def create(self, validated_data):
        if 'title' in validated_data and len(validated_data['title']):
            event = Event.objects.create(title=validated_data['title'])
        else:
            event = Event.objects.create()
        for party in validated_data.get('parties'):
            party_obj = User.objects.get_or_create(email=party)
            user = party_obj[0]
            if party_obj[1]: # Created
                user.username = user.email
                user.is_active = False
                user.save()
            event.parties.add(user)
        for slot in validated_data.get('slots'):
            TimeSpan.objects.create(event=event, **slot)
        return event

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            instance.title = validated_data['title']
            instance.save()
        slots_remain = []
        if 'slots' not in validated_data:
            raise serializers.ValidationError(
                {'slots': ['This field is required']})
        for slot in validated_data['slots']:
            try:
                found = instance.slots.get(**slot)
                slots_remain.append(found.id)
            except TimeSpan.DoesNotExist:
                slot['event_id'] = instance.id
                obj = TimeSpan.objects.create(**slot)
                instance.slots.add(obj)
                slots_remain.append(obj.id)
        for slot in instance.slots.all():
            if slot.id not in slots_remain:
                slot.delete()
        return instance
         

class EventNotifySerializer(serializers.Serializer):
    sender = UserSerializer()
    parties = UserSerializer(many=True)
    slots = TimeSpanSerializer(many=True)
    log_url = serializers.HyperlinkedIdentityField(
        view_name='dispatch-log')
    notify_url = serializers.HyperlinkedIdentityField(
        view_name='event-notify')
    event_url = serializers.HyperlinkedIdentityField(
        view_name='event-detail')

    def validate(self, data):
        event = self.instance
        invalid_sender = False
        errors = {}
        try:
            sender_obj = User.objects.get(email=data['sender'])
            if sender_obj not in event.parties.all():
                invalid_sender = True
        except User.DoesNotExist:
            invalid_sender = True
        if invalid_sender:
            errors['sender'] = ['Not in event: ' + data['sender']]
        invalid_emails = []
        for event_party in data['parties']:
            try: 
                party_obj = User.objects.get(email=event_party)
                if party_obj not in event.parties.all():
                    invalid_emails.append(event_party)
            except User.DoesNotExist:
                # X: Non-esixtent user reports only absence from event 
                invalid_emails.append(event_party)
        if len(invalid_emails):
            errors['parties'] = ['Not in event: ' + ' '.join(invalid_emails)]
            #[f'Not in event: {e}' for e in invalid_emails]}
        event_slots = event.slots.all()
        valid_slots = 0
        for slot in data['slots']:
            try:
                event.slots.get(**slot)
                valid_slots += 1
            except TimeSpan.DoesNotExist:
                pass
        if len(event_slots) != valid_slots:
            errors['slots'] = ['Mismatch with event'] 
        if len(errors) > 0:
            raise serializers.ValidationError(errors)
        return data 


class DispatchLogEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = DispatchLogEntry
        fields = ['id', 'when', 'occurrence', 'effector', 'slots', 'data']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['slots'] = json.loads(data['slots'])
        data['data'] = json.loads(data['data'])
        return data

    def to_internal_value(self, data):
        data['slots'] = json.dumps(data['slots'])
        data['data'] = json.dumps(data['data'])
        return data
    
    def create(self, validated_data):
        entry = DispatchLogEntry.objects.create(**validated_data)
        return entry


class DispatchLogSerializer(serializers.Serializer):
    # X: ?
    #event = serializers.HyperlinkedIdentityField(view_name='event-detail')
    #event_url = serializers.HyperlinkedRelatedField(read_only=True,
    event = serializers.HyperlinkedRelatedField(read_only=True,
        view_name='event-detail')
    parties = UserSerializer(many=True)
    entries = DispatchLogEntrySerializer(many=True)



