# Generated by Django 3.1.1 on 2020-09-14 23:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0005_auto_20200914_0353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfoller',
            name='phone_number',
        ),
    ]