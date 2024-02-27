from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from station.models import Station, Route, TrainType, Train, Crew, Journey


ROUTE_URL = reverse("station:route-list")
JOURNEY_URL = reverse("station:journey-list")


class JourneyModelTests(TestCase):
    def setUp(self):
        self.station1 = Station.objects.create(
            name="Station 1", latitude=35.45, longitude=25.55
        )
        self.station2 = Station.objects.create(
            name="Station 2", latitude=35.45, longitude=25.55
        )
        self.route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=500
        )
        self.train_type = TrainType.objects.create(name="Train")
        self.train = Train.objects.create(
            name="Train 1", cargo_num=5, places_in_cargo=5, train_type=self.train_type
        )
        self.crew1 = Crew.objects.create(first_name="John", last_name="Doe")
        self.departure_time = timezone.now()
        self.arrival_time = self.departure_time + timezone.timedelta(hours=2)

    def test_journey_creation(self):
        journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time,
        )
        journey.crews.add(self.crew1)

        self.assertTrue(isinstance(journey, Journey))


def sample_route(**params):
    defaults = {
        "source": Station.objects.create(
            name="Source Station", latitude=0.0, longitude=0.0
        ),
        "destination": Station.objects.create(
            name="Destination Station", latitude=1.0, longitude=1.0
        ),
        "distance": 100,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def image_upload_url(train_id):
    """Return URL for recipe image upload"""
    return reverse("station:train-upload-image", args=[train_id])


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_filter_routes_by_source(self):
        source1 = Station.objects.create(name="Source 1", latitude=10.0, longitude=20.0)
        source2 = Station.objects.create(name="Source 2", latitude=15.0, longitude=25.0)

        route1 = sample_route(source=source1)
        route2 = sample_route(source=source2)

        res1 = self.client.get(ROUTE_URL, {"source": source1.id})
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res1.data), 1)
        self.assertTrue(any(route["id"] == route1.id for route in res1.data))

        res2 = self.client.get(ROUTE_URL, {"source": source2.id})
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res2.data), 1)
        self.assertTrue(any(route["id"] == route2.id for route in res2.data))


def create_sample_station(name="Station", latitude=1.0, longitude=2.0):
    return Station.objects.create(name=name, latitude=latitude, longitude=longitude)


def create_sample_route(source, destination, distance=100):
    return Route.objects.create(
        source=source, destination=destination, distance=distance
    )


def create_sample_traintype(name="TrainType"):
    return TrainType.objects.create(name=name)


def create_sample_train(
    train_type,
    name="TrainName",
    cargo_num=1,
    places_in_cargo=5,
):
    return Train.objects.create(
        train_type=train_type,
        name=name,
        cargo_num=cargo_num,
        places_in_cargo=places_in_cargo,
    )


def create_sample_journey(
    route,
    train,
    departure_time=timezone.now(),
    arrival_time=timezone.now() + timedelta(hours=1),
):
    return Journey.objects.create(
        route=route,
        train=train,
        departure_time=departure_time,
        arrival_time=arrival_time,
    )


class UnauthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_filter_journeys_by_train(self):
        station1 = create_sample_station(name="Station 1")
        station2 = create_sample_station(name="Station 2")
        route = create_sample_route(source=station1, destination=station2)
        train_type = create_sample_traintype(name="Train 1")
        train1 = create_sample_train(name="Train 1", train_type=train_type)
        train2 = create_sample_train(name="Train 2", train_type=train_type)
        journey1 = create_sample_journey(route=route, train=train1)
        journey2 = create_sample_journey(route=route, train=train2)

        self.filter_journeys_by_train_and_assert(train1.id, journey1.id)
        self.filter_journeys_by_train_and_assert(train2.id, journey2.id)

    def filter_journeys_by_train_and_assert(self, train_id, journey_id):
        res = self.client.get(JOURNEY_URL, {"train": train_id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id"], journey_id)
