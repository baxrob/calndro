# Generated by Django 3.2.9 on 2022-02-06 19:16

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedul', '0004_auto_20220204_1734'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailToken',
            fields=[
                ('key', models.CharField(editable=False, max_length=40, primary_key=True, serialize=False)),
                ('expires', models.DateTimeField(default=datetime.datetime(2022, 2, 11, 19, 16, 51, 736388), editable=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedul.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]