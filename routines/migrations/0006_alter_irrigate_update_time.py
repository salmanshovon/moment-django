# Generated by Django 5.1.6 on 2025-03-26 11:29

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routines', '0005_irrigate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='irrigate',
            name='update_time',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='When the record was last updated'),
        ),
    ]
