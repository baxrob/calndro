# Generated by Django 3.2.9 on 2022-02-04 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedul', '0003_event_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timespan',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slots', to='schedul.event'),
        ),
        migrations.CreateModel(
            name='DispatchLogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('occurrence', models.CharField(choices=[('UPDATE', 'Update'), ('NOTIFY', 'Notify'), ('VIEW', 'View')], max_length=32)),
                ('effector', models.CharField(max_length=128)),
                ('slots', models.CharField(max_length=1024)),
                ('data', models.CharField(default='{}', max_length=128)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dispatch_log', to='schedul.event')),
            ],
        ),
    ]
