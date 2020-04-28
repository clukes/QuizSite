# Generated by Django 2.1.3 on 2020-04-28 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_auto_20200428_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField(max_length=300)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='round',
            name='background_image_url',
            field=models.URLField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='genericquestion',
            name='type',
            field=models.CharField(choices=[('t', 'Text'), ('i', 'Image'), ('m', 'Multiple Choice')], default='t', max_length=1),
        ),
    ]
