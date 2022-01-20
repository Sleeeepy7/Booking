from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, serializers
from rest_framework.serializers import ModelSerializer

from .models import Office, Bookings

User = get_user_model()


class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        """ Создания пользователя в бд"""
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class OfficeSerializer(ModelSerializer):
    class Meta:
        model = Office
        fields = ('info',)


class BookingSerializer(ModelSerializer):
    class Meta:
        model = Bookings
        fields = ('date_from', 'date_to', 'owner', 'office', 'book_info')

    """ Используется для отображения юзера, который забронил """
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)

    def create(self, validated_data):
        date_from = validated_data['date_from']
        date_to = validated_data['date_to']
        office = validated_data['office']
        if date_from >= date_to:
            raise serializers.ValidationError({"date_to": "конечная дата должна быть позже начальной"})
        booked_1 = Bookings.objects.select_related().filter(
            Q(date_from__range=(date_from, date_to)) | Q(
                date_to__range=(date_to, date_to)), office=office)
        booked_2 = Bookings.objects.select_related().filter(
            date_from__lte=date_from, date_to__gte=date_to, office=office)
        booked_3 = Bookings.objects.select_related().filter(
            date_from__lte=date_to,
            date_to__gte=date_from,
            office=office)

        booked = booked_1.exists() | booked_2.exists() | booked_3.exists()
        if booked:
            raise serializers.ValidationError(code=status.HTTP_400_BAD_REQUEST)
        return Bookings.objects.create(**validated_data)
