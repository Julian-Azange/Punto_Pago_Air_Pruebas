# Generated by Django 5.1.3 on 2024-11-26 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0005_alter_flight_available_seats_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='seat',
            unique_together={('airplane', 'seat_number')},
        ),
    ]
