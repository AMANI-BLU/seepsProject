# Generated by Django 5.0.2 on 2024-04-15 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seepsApp', '0028_user_is_verified_alter_exam_difficulty'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verification_token',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='verification token'),
        ),
    ]