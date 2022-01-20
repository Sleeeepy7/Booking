
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OfficeBookingViewSet, CreateUserView, BookingsViewSet, view_free_office, get_offices

bookings = DefaultRouter()
office_booking = DefaultRouter()
register_user = DefaultRouter()

bookings.register('bookings', BookingsViewSet, basename='bookings')
office_booking.register('booking', OfficeBookingViewSet, basename='booking')
register_user.register('registration', CreateUserView, basename='registration')

urlpatterns = [
    path('', include(register_user.urls)),
    path('', include(bookings.urls)),
    path('offices/', get_offices, name='list_offices'),
    path('office/<int:office_id>/', include(office_booking.urls),
         name='booking'),  # резервирование выбранного места
    path('offices/free', view_free_office, name='free_offices'),
    path('auth/', include('rest_framework.urls')),
]
