from django.contrib import admin
from schedul.models import Event, TimeSpan, DispatchLogEntry


#class PartiesInline(admin.StackedInline):
class PartiesInline(admin.TabularInline):
    model = Event.parties.through
    extra = 1


class TimeSpanInline(admin.TabularInline):
    model = TimeSpan


class EventAdmin(admin.ModelAdmin):

    actions_on_top = True
    actions_on_bottom = True

    inlines = [PartiesInline, TimeSpanInline]
    #inlines = [TimeSpanInline]
    #exclude = ['parties']
    filter_horizontal = ['parties']

    save_on_top = True
    search_fields = ['parties__email']

    list_display = ['id', 'title', 'party_emails', 'span_count']
    #list_display_links = ['id', 'title', 'party_emails', 'span_count']
    list_display_links = ['id', 'title']
    ordering = ['id']

    def party_emails(self, obj):
        return ' '.join([p.email for p in obj.parties.all()])
    #party_emails.short_description = 'foo'

    #@admin.display(description='bar', empty_value='nil')
    def span_count(self, obj):
        return obj.slots.count()


admin.site.register(Event, EventAdmin)

class DispatchLogEntryAdmin(admin.ModelAdmin):
    list_display = ['event_title', 'event', 'occurrence', 'when', 'effector']
    readonly_fields = ['event', 'occurrence', 'when', 'effector', 'slots', 'data']
    #readonly_fields = ['when']
    ordering = ['event', '-when']

    def event_title(self, obj):
        return obj.event.title 

    # X: ?
    @admin.display
    def slots(self):
        return 'foo'
        return self.slots
        return json.dumps(self.slots)

admin.site.register(DispatchLogEntry, DispatchLogEntryAdmin)
