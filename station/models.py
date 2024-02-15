from django.contrib.auth.models import User


import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Station(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, related_name="departure_station", on_delete=models.CASCADE
    )
    destination = models.ForeignKey(
        Station, related_name="arrival_station", on_delete=models.CASCADE
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination}  ({self.distance} km)"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return self.first_name + " " + self.last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class TrainType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def train_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/train_images/", filename)


class Train(models.Model):
    name = models.CharField(max_length=100)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=train_image_file_path)

    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return self.name


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, related_name="journey")

    class Meta:
        verbose_name_plural = "journey"
        ordering = ["-departure_time"]

    def __str__(self):
        return self.train.name + " " + str(self.departure_time)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("cargo", "seat", "journey")
        ordering = (
            "cargo",
            "seat",
        )

    def __str__(self):
        return f"{self.journey} - (seat: {self.seat})"

    @staticmethod
    def validate_cargo(cargo: int, cargo_num: int, error_to_raise):
        if not (1 <= cargo <= cargo_num):
            raise error_to_raise(
                {"cargo": f"Cargo must be in range [1, {cargo_num}], not {cargo}"}
            )

    @staticmethod
    def validate_seat(seat: int, places_in_cargo: int, error_to_raise):
        if not (1 <= seat <= places_in_cargo):
            raise error_to_raise(
                {"cargo": f"Seat must be in range [1, {places_in_cargo}], not {seat}"}
            )

    def clean(self):
        Ticket.validate_cargo(self.cargo, self.journey.train.cargo_num, ValidationError)
        Ticket.validate_seat(
            self.seat, self.journey.train.places_in_cargo, ValidationError
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    # @staticmethod
    # def validate_ticket(cargo, seat, train):
    #     for ticket_attr_value, ticket_attr_name, train_attr_name in [
    #         ("cargo", "cargo", "cargo_num"),
    #         ("seat", "seat", "places_in_cargo"),
    #     ]:
    #         count_attrs = getattr(train, train_attr_name)
    #         if not (1 <= ticket_attr_value <= count_attrs):
    #             raise ValidationError(
    #                 {
    #                     ticket_attr_name: f"{ticket_attr_name} "
    #                                       f"number must be in available range: "
    #                                       f"(1, {train_attr_name}): "
    #                                       f"(1, {count_attrs})"
    #                 }
    #             )
    #
    # def clean(self):
    #     Ticket.validate_ticket(
    #         self.cargo,
    #         self.seat,
    #         self.journey.train,
    #         ValidationError,
    #     )
    #
    # def save(
    #         self,
    #         force_insert=False,
    #         force_update=False,
    #         using=None,
    #         update_fields=None,
    # ):
    #     self.full_clean()
    #     return super(Ticket, self).save(
    #         force_insert, force_update, using, update_fields
    #         )
    #
    # def __str__(self):
    #     return (f"{str(self.journey)} (cargo: {self.cargo}, seat: {self.seat})")

    # def clean(self):
    #     if not (1 <= self.cargo <= self.journey.train.cargo_num):
    #         raise ValidationError({"cargo": "Cargo number is out of bounds"})
    #
    #     if not (1 <= self.seat <= self.journey.train.places_in_cargo):
    #         raise ValidationError({"seat": "Seat number is out of bounds"})
    #
    #     existing_tickets = Ticket.objects.filter(
    #         journey=self.journey,
    #         cargo=self.cargo,
    #         seat=self.seat
    #     )
    #
    #     if self.pk:
    #         existing_tickets = existing_tickets.exclude(pk=self.pk)
    #     if existing_tickets.exists():
    #         raise ValidationError("Ticket already exists")
    #
    #     def save(self, *args, **kwargs):
    #         self.full_clean()
    #         super().save(*args, **kwargs)
