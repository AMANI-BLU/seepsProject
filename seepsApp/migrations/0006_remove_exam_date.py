# Generated by Django 5.0.1 on 2024-02-24 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seepsApp', '0005_exam'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exam',
            name='date',
        ),
    ]
