# Generated by Django 5.1.5 on 2025-02-18 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_publictaskcategory_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publictaskcategory',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='publictaskcategory',
            name='updated_at',
        ),
    ]
