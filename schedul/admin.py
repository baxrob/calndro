from django.contrib import admin
from schedul.models import Event, TimeSpan


#class PartiesInline(admin.TabularInline):
class PartiesInline(admin.StackedInline):
    model = Event.parties.through
    extra = 1

class TimeSpanInline(admin.TabularInline):
    model = TimeSpan

class EventAdmin(admin.ModelAdmin):
    inlines = [PartiesInline, TimeSpanInline]
    exclude = ['parties']

admin.site.register(Event, EventAdmin)
