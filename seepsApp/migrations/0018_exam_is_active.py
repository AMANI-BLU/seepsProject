# Generated by Django 5.0.2 on 2024-03-11 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seepsApp', '0017_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
