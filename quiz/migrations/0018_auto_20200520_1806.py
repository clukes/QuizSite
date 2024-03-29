# Generated by Django 2.1.3 on 2020-05-20 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0017_auto_20200520_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressiveStage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('media_url', models.URLField(blank=True, max_length=1000, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='progressivequestion',
            name='max_points',
            field=models.DecimalField(decimal_places=2, default=3, max_digits=10),
        ),
        migrations.AddField(
            model_name='progressivequestion',
            name='min_points',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='genericquestion',
            name='question_type',
            field=models.CharField(choices=[('t', 'Text Question'), ('m', 'Multiple Choice Question'), ('p', 'Progressive Question')], default='t', max_length=1),
        ),
        migrations.AddField(
            model_name='progressivestage',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='quiz.ProgressiveQuestion'),
        ),
    ]
