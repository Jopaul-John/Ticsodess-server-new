# Generated by Django 3.0.4 on 2020-03-15 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticsodessapp', '0009_auto_20200314_1656'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game_model',
            name='score_o',
        ),
        migrations.RemoveField(
            model_name='game_model',
            name='score_x',
        ),
        migrations.AddField(
            model_name='game_model',
            name='winner',
            field=models.CharField(blank=True, max_length=1),
        ),
    ]