# Generated by Django 5.1.6 on 2025-02-19 11:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_alter_task_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskcategory',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='taskcategory',
            name='updated_at',
        ),
    ]
