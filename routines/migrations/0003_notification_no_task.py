# Generated by Django 5.1.6 on 2025-03-21 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routines', '0002_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='no_task',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
