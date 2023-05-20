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
        return data


class TimeSpanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TimeSpan
        fields = ['begin', 'duration']


class EventSerializer(serializers.HyperlinkedModelSerializer):
    parties = UserSerializer(many=True, allow_empty=False)
    # 30 <= logentry.slots char len / slot len = 2048 / 65 
    slots = TimeSpanSerializer(many=True, max_length=30)
    log_url = serializers.HyperlinkedIdentityField(
        view_name='dispatch-log')
    notify_url = serializers.HyperlinkedIdentityField(
        view_name='event-notify')

    class Meta:
        model = Event
        fields = ['id', 'url', 'log_url', 'title', 'parties', 'slots', 
            'notify_url']
        read_only_fields = ['parties']

    def create(self, validated_data):
        if 'title' in validated_data and len(validated_data.get('title')):
            event = Event.objects.create(title=validated_data.get('title'))
        else:
            event = Event.objects.create()
        for party in validated_data.get('parties'):
            user, created = User.objects.get_or_create(email=party)
            if created:
                user.username = user.email
                user.is_active = False
                user.save()
            event.parties.add(user)
        for slot in validated_data.get('slots'):
            TimeSpan.objects.create(event=event, **slot)
        return event

    def update(self, instance, validated_data):
        if not validated_data:
            raise serializers.ValidationError(['No update data'])
        if 'title' in validated_data:
            instance.title = validated_data.get('title')
            instance.save()
        #if 'slots' not in validated_data:
        #    raise serializers.ValidationError(
        #        {'slots': ['This field is required']})
        #import ipdb; ipdb.set_trace()
        if 'slots' in validated_data:
            slots_remain = []
            for slot in validated_data.get('slots'):
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
        '''
        slots_remain = []
        for slot in validated_data.get('slots'):
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
        '''
        return instance
         

class EventNotifySerializer(serializers.Serializer):
    sender = UserSerializer(required=False)
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

        # X: 
        try:
            sender_obj = User.objects.get(email=data['sender'])
            if (sender_obj not in event.parties.all() 
                and not sender_obj.is_staff):
                invalid_sender = True
        except KeyError:
            # Allow empty sender
            pass
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
                # X: Non-existent user reports only absence from event 
                invalid_emails.append(event_party)
        if len(invalid_emails):
            errors['parties'] = ['Not in event: ' + ' '.join(invalid_emails)]
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
        if any(errors):
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
    event = serializers.HyperlinkedRelatedField(read_only=True,
        view_name='event-detail')
    parties = UserSerializer(many=True)
    entries = DispatchLogEntrySerializer(many=True)



