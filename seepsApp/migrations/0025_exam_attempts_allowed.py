# Generated by Django 5.0.2 on 2024-04-04 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seepsApp', '0024_question_answer_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='attempts_allowed',
            field=models.IntegerField(default=3),
        ),
    ]