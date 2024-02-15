from django.db import transaction

from rest_framework import serializers
from station.models import (
    Station,
    Route,
    Crew,
    TrainType,
    Train,
    Journey,
    Order,
    Ticket,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


#
#


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = serializers.CharField(source="train_type.name")

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
        )


class TrainDetailSerializer(TrainSerializer):

    class Meta:
        model = Train
        fields = ("id", "name")


class TrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "image")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_cargo(
            attrs["cargo"],
            attrs["journey"].train.cargo_num,
            serializers.ValidationError,
        )
        Ticket.validate_seat(
            attrs["seat"],
            attrs["journey"].train.places_in_cargo,
            serializers.ValidationError,
        )

        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")


class JourneySerializer(serializers.ModelSerializer):

    class Meta:
        model = Journey
        fields = ("id", "train", "departure_time", "arrival_time", "route", "crews")


class JourneyListSerializer(JourneySerializer):
    train = TrainSerializer(many=False, read_only=True)
    route_distance = serializers.IntegerField(source="route.distance")
    crews = serializers.StringRelatedField(many=True, read_only=True)

    train_places_in_cargo = serializers.IntegerField(
        source="train.places_in_cargo", read_only=True
    )
    tickets_taken = serializers.IntegerField(source="tickets.count")

    tickets_available = serializers.IntegerField(read_only=True)
    tickets_places_in_cargo = serializers.IntegerField(read_only=True)
    tickets_cargo_num = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "train",
            "departure_time",
            "arrival_time",
            "route_distance",
            "crews",
            "train_places_in_cargo",
            "tickets_taken",
            "tickets_available",
            "tickets_places_in_cargo",
            "tickets_cargo_num",
        )
        # fields = ("id", "train", "departure_time", "arrival_time", "route_distance", "crews", "tickets_available")


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)


class JourneyDetailSerializer(JourneySerializer):
    route = RouteSerializer(many=False, read_only=True)
    crews = CrewSerializer(many=True, read_only=True)
    # tickets = TicketSerializer(many=True, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        source="tickets", many=True, read_only=True, slug_field="seat"
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "train",
            "departure_time",
            "arrival_time",
            "route",
            "crews",
            "taken_seats",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
