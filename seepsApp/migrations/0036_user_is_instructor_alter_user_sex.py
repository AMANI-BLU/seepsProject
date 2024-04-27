# Generated by Django 5.0.2 on 2024-04-25 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seepsApp', '0035_examsubmission_exam_submitted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_instructor',
            field=models.BooleanField(default=False, verbose_name='Is instructor'),
        ),
        migrations.AlterField(
            model_name='user',
            name='sex',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female')], max_length=10, null=True),
        ),
    ]