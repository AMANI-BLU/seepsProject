# Generated by Django 5.0.2 on 2024-04-27 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seepsApp', '0038_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorial',
            name='added_by',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]