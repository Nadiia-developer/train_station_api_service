from django.contrib import admin
from .models import (
    Station,
    Route,
    Crew,
    TrainType,
    Train,
    Journey,
    Order,
    Ticket
)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "latitude", "longitude")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "distance")
    search_fields = ("source__name", "destination__name")


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name")


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cargo_num", "places_in_cargo", "train_type")
    search_fields = ("name", "train_type__name")


@admin.register(Journey)
class JourneyAdminAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "train", "departure_time", "arrival_time")
    list_filter = ("departure_time", "arrival_time")
    search_fields = ("route__source__name", "route__destination__name")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "cargo", "seat", "journey", "order")
    list_filter = ("journey",)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)
    list_display = ("id", "created_at", "user")
    list_filter = ("created_at",)
    search_fields = ("user__username",)
