# Generated by Django 2.1.3 on 2020-06-27 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0038_auto_20200627_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='finalresults',
            name='draw',
            field=models.BooleanField(default=False),
        ),
    ]