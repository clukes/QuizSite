# Generated by Django 2.1.3 on 2020-05-21 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0028_textresponse_max_points'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textresponse',
            name='max_points',
        ),
        migrations.AddField(
            model_name='genericresponse',
            name='max_points',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
    ]
