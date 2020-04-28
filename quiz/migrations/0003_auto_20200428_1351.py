# Generated by Django 2.1.3 on 2020-04-28 12:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('quiz', '0002_auto_20200428_1348'),
    ]

    operations = [
        migrations.RenameField(
            model_name='genericquestion',
            old_name='detail_content_type',
            new_name='content_type',
        ),
        migrations.RenameField(
            model_name='genericquestion',
            old_name='detail_object_id',
            new_name='object_id',
        ),
        migrations.AlterUniqueTogether(
            name='genericquestion',
            unique_together={('content_type', 'object_id'), ('number', 'round')},
        ),
    ]
