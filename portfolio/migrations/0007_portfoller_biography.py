# Generated by Django 3.1.1 on 2020-09-15 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_remove_portfoller_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoller',
            name='biography',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]