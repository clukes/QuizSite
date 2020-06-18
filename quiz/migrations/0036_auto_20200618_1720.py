# Generated by Django 2.1.3 on 2020-06-18 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0035_auto_20200617_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genericresponse',
            name='type',
            field=models.CharField(choices=[('t', 'Text'), ('w', 'Map')], default='t', max_length=1),
        ),
        migrations.AlterField(
            model_name='mapquestion',
            name='map',
            field=models.CharField(default='world_mill', max_length=100),
        ),
    ]
