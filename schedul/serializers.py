from django.contrib.auth import get_user_model
from rest_framework import serializers

from schedul.models import Event, TimeSpan


User = get_user_model()

class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()


class TimeSpanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TimeSpan
        fields = ['begin', 'duration']


class EventSerializer(serializers.ModelSerializer):
    parties = UserSerializer(many=True)
    span = TimeSpanSerializer(many=True)

    class Meta:
        model = Event
        fields = ['id', 'parties', 'span']
        #read_only_fields = ['parties']

    def create(self, validated_data):
        event = Event.objects.create()
        for party in validated_data.get('parties'):
            party_obj = User.objects.get_or_create(email=party['email'])[0]
            event.parties.add(party_obj)
        for span in validated_data.get('span'):
            TimeSpan.objects.create(event=event, **span)
        return event

    def update(self, instance, validated_data):
        remain = []
        #print(validated_data)
        #import ipdb; ipdb.set_trace()
        if 'span' not in validated_data:
            raise serializers.ValidationError(
                {'span': ['This field is required']})
        for span in validated_data['span']:
            try:
                found = instance.span.get(**span)
                remain.append(found.id)
            #except Event.DoesNotExist:
            except TimeSpan.DoesNotExist:
                #import ipdb; ipdb.set_trace()
                span['event_id'] = instance.id
                obj = TimeSpan.objects.create(**span)
                instance.span.add(obj)
                remain.append(obj.id)
        for span in instance.span.all():
            if span.id not in remain:
                span.delete()
        return instance
         
