from datetime import datetime

import pytz
from django.contrib.auth import get_user_model
from rest_framework import mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import Q

from booking import settings
from .models import Bookings, Office
from .permissions import IsOwnerOrReadOnly, IsAdminUserOrReadOnly
from .serializers import OfficeSerializer, BookingSerializer, UserSerializer

User = get_user_model()


class CreateUserView(mixins.CreateModelMixin, GenericViewSet):
    """ Регистрация пользователей """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class OfficeBookingViewSet(ModelViewSet):
    """Бронирование конкретного помещения"""
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    serializer_class = BookingSerializer

    def get_queryset(self):
        office_id = self.kwargs['office_id']
        office = get_object_or_404(Office.objects.prefetch_related('booking'),
                                   id=office_id)
        return office.booking.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUserOrReadOnly])
def get_offices(request):
    """Список всех помещений."""
    if request.method == 'GET':
        offices = Office.objects.all()
        serializer = OfficeSerializer(offices, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = OfficeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingsViewSet(ModelViewSet):
    """Бронирование """
    queryset = Bookings.objects.all()
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        print(serializer.validated_data)
        serializer.save(owner=self.request.user)


@api_view(['GET'])
def view_free_office(request):
    """Просмотр свободных помещений за период времени."""
    if request.method == 'GET':
        if request.GET:
            get_date_from = request.GET.get('datetime_from')
            get_date_to = request.GET.get('datetime_to')
            if get_date_from and get_date_to:
                get_date_from = get_date_from
                get_date_to = get_date_to
                date_format = '%Y-%m-%dT%H:%M'

                try:
                    date_from = datetime.strptime(get_date_from, date_format)
                    date_to = datetime.strptime(get_date_to, date_format)

                    tz = pytz.timezone(settings.TIME_ZONE)
                    date_from = tz.localize(date_from)
                    date_to = tz.localize(date_to)

                except Exception as exc:
                    print('---except---', exc)
                    return Response({'error GET': ('формат ввода '
                                                   'datetime_from=2021-01-08T13:00&'
                                                   'datetime_to=2021-01-08T15:00')})

                free_offices = Office.objects.prefetch_related(
                    'booking').exclude(
                    Q(booking__date_from__range=(date_from, date_to)) | Q(
                        booking__date_to__range=(date_to, date_to))
                ).exclude(
                    booking__date_from__lte=date_from,
                    booking__date_to__gte=date_to
                ).exclude(
                    booking__date_from__lte=date_to,
                    booking__date_to__gte=date_from
                )
                serializer = OfficeSerializer(free_offices, many=True)
                return Response(serializer.data)
        return Response({'error GET': ('формат ввода '
                                       'datetime_from=2021-01-08T13:00&'
                                       'datetime_to=2021-01-08T15:00')})
