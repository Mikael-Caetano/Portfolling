# Generated by Django 3.1.1 on 2020-11-12 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoller',
            name='career',
            field=models.CharField(choices=[('Developer', 'Developer'), ('Artist', 'Artist'), ('Writer', 'Writer')], default='Developer', max_length=20),
        ),
    ]