# Generated by Django 2.1.3 on 2020-04-19 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_auto_20200419_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='marking',
            field=models.BooleanField(default=False),
        ),
    ]
