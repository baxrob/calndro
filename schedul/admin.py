from django.contrib import admin
from schedul.models import Event, TimeSpan, EmailToken, DispatchLogEntry


#class PartiesInline(admin.StackedInline):
class PartiesInline(admin.TabularInline):
    model = Event.parties.through
    max_num = 0
    fields = ['user', 'email']
    readonly_fields = ['user', 'email']
    can_delete = False
    verbose_name = 'Parties'

    def email(self, instance):
        #import ipdb; ipdb.set_trace()
        return instance.user.email


class TimeSpanInline(admin.TabularInline):
    model = TimeSpan


class EmailTokenInline(admin.TabularInline):
#class EmailTokenInline(admin.StackedInline):
    model = EmailToken
    readonly_fields = ('key', 'user', 'expires')
    #readonly_fields
    extra = 0


class EventAdmin(admin.ModelAdmin):

    actions_on_top = True
    actions_on_bottom = True

    inlines = [PartiesInline, TimeSpanInline, EmailTokenInline]
    #inlines = [TimeSpanInline, EmailTokenInline]
    #inlines = [TimeSpanInline]
    exclude = ['parties']
    #filter_horizontal = ['parties']
    #readonly_fields = ('parties',)
    fields = []

    save_on_top = True
    search_fields = ['parties__email']
    #readonly_fields = ['toke

    list_display = ['id', 'title', 'party_emails', 'slot_count']
    #list_display_links = ['id', 'title', 'party_emails', 'span_count']
    list_display_links = ['id', 'title']
    ordering = ['id']

    def party_emails(self, obj):
        return ' '.join([p.email for p in obj.parties.all()])
    #party_emails.short_description = 'foo'

    #@admin.display(description='bar', empty_value='nil')
    def slot_count(self, obj):
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
