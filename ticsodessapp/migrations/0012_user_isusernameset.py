# Generated by Django 3.0.4 on 2020-10-19 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticsodessapp', '0011_auto_20200322_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='isUsernameSet',
            field=models.BooleanField(default=False),
        ),
    ]
