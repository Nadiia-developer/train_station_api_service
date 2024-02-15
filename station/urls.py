from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StationViewSet,
    RouteViewSet,
    CrewViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    JourneyViewSet,
    OrderViewSet,
    TicketViewSet,
)


router = DefaultRouter()
router.register(r"stations", StationViewSet, basename="station")
router.register(r"routes", RouteViewSet, basename="route")
router.register(r"crews", CrewViewSet, basename="crew")
router.register(r"traintypes", TrainTypeViewSet, basename="traintype")
router.register(r"trains", TrainViewSet, basename="train")
router.register(r"journeys", JourneyViewSet, basename="journey")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"tickets", TicketViewSet, basename="ticket")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "station"
