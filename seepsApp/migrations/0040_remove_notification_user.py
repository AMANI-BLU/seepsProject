# Generated by Django 5.0.2 on 2024-04-27 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seepsApp', '0039_tutorial_added_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='user',
        ),
    ]
