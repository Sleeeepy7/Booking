from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Office(models.Model):
    info = models.TextField(verbose_name='Информация о помещении', null=True)

    def __str__(self):
        return f'Помещение номер {self.id}'

    class Meta:
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'


class Bookings(models.Model):
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    owner = models.ForeignKey(User, related_name='booking',
                              on_delete=models.CASCADE, verbose_name='Бронирующий')
    office = models.ForeignKey(Office, related_name='booking',
                               on_delete=models.CASCADE, verbose_name='Помещение')
    book_info = models.TextField(verbose_name="Информация о бронировании")

    def __str__(self):
        return f'Помещение номер {self.office.id}: Бронь номер {self.id}'

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирование'
