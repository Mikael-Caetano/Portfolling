# Generated by Django 3.1.1 on 2020-09-14 06:53

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0004_auto_20200914_0125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoller',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, region=None),
        ),
    ]