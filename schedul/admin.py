from django.contrib import admin
from django.utils import timezone
from schedul.models import Event, TimeSpan, EmailToken, DispatchLogEntry


admin.site.site_header = 'cal_dor^io'

#class PartiesInline(admin.StackedInline):
class PartiesInline(admin.TabularInline):
    model = Event.parties.through
    max_num = 0
    fields = ['user', 'email']
    readonly_fields = ['user', 'email']
    can_delete = False
    verbose_name = 'Parties'

    def email(self, instance):
        return instance.user.email


class TimeSpanInline(admin.TabularInline):
    model = TimeSpan

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # X: ?? this has global effects ?
        #timezone.activate('America/Los_Angeles')


class EmailTokenInline(admin.TabularInline):
#class EmailTokenInline(admin.StackedInline):
    model = EmailToken
    readonly_fields = ('key', 'user', 'expires')
    extra = 0


class DispatchLogInline(admin.TabularInline):
    model = DispatchLogEntry
    readonly_fields = ['event', 'occurrence', 'when', 'effector', 'slots',
        'when', 'data']
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

class EventAdmin(admin.ModelAdmin):

    actions_on_top = True
    actions_on_bottom = True

    inlines = [PartiesInline, TimeSpanInline, EmailTokenInline,
        DispatchLogInline]
    exclude = ['parties']
    fields = []

    save_on_top = True
    search_fields = ['parties__email']

    list_display = ['id', 'title', 'party_emails', 'slot_count']
    list_display_links = ['id', 'title']
    ordering = ['id']

    def party_emails(self, obj):
        return ' '.join([p.email for p in obj.parties.all()])

    def slot_count(self, obj):
        return obj.slots.count()

admin.site.register(Event, EventAdmin)


class DispatchLogEntryAdmin(admin.ModelAdmin):
    list_display = ['event_title', 'event', 'occurrence', 'when', 'effector']
    readonly_fields = ['event', 'occurrence', 'when', 'effector', 'slots',
        'data']
    ordering = ['event', '-when']

    def event_title(self, obj):
        return obj.event.title 

admin.site.register(DispatchLogEntry, DispatchLogEntryAdmin)
