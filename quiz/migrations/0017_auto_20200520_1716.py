# Generated by Django 2.1.3 on 2020-05-20 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0016_remove_game_timerlength'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressiveQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='genericquestion',
            name='multiple_choice',
        ),
        migrations.RemoveField(
            model_name='genericquestion',
            name='type',
        ),
        migrations.AddField(
            model_name='genericquestion',
            name='media_type',
            field=models.CharField(choices=[('n', 'None'), ('i', 'Image'), ('v', 'Video'), ('a', 'Audio')], default='n', max_length=1),
        ),
        migrations.AddField(
            model_name='genericquestion',
            name='question_type',
            field=models.CharField(choices=[('t', 'Text'), ('m', 'Multiple Choice'), ('p', 'Progressive')], default='t', max_length=1),
        ),
    ]
