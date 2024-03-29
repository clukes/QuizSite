# Generated by Django 2.1.3 on 2020-04-28 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('quiz', '0003_auto_20200428_1351'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marking', models.CharField(choices=[('c', 'Correct'), ('i', 'Incorrect'), ('p', 'Partial')], default='i', max_length=1)),
                ('points', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('type', models.CharField(choices=[('t', 'Text')], default='t', max_length=1)),
                ('object_id', models.IntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Game')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.GenericQuestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.User')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='textresponse',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='textresponse',
            name='game',
        ),
        migrations.RemoveField(
            model_name='textresponse',
            name='marking',
        ),
        migrations.RemoveField(
            model_name='textresponse',
            name='points',
        ),
        migrations.RemoveField(
            model_name='textresponse',
            name='question',
        ),
        migrations.RemoveField(
            model_name='textresponse',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='genericresponse',
            unique_together={('content_type', 'object_id'), ('question', 'user', 'game')},
        ),
    ]
