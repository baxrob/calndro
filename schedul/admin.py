from django.contrib import admin
from schedul.models import Event, TimeSpan


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

    list_display = ['id', 'party_emails', 'span_count']
    list_display_links = ['id', 'party_emails', 'span_count']
    ordering = ['id']

    def party_emails(self, obj):
        return ' '.join([p.email for p in obj.parties.all()])
    #party_emails.short_description = 'foo'

    #@admin.display(description='bar', empty_value='nil')
    def span_count(self, obj):
        return obj.span.count()

admin.site.register(Event, EventAdmin)
