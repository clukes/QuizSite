# Generated by Django 2.1.3 on 2020-05-20 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0021_auto_20200520_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='progressivequestion',
            name='step',
            field=models.DecimalField(decimal_places=2, default=0.5, max_digits=10),
        ),
    ]
