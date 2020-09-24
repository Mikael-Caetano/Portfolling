# Generated by Django 3.1.1 on 2020-09-11 18:11

from django.db import migrations, models
import django.db.models.deletion
import portfolio.models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfoller',
            name='projects_count',
        ),
        migrations.AddField(
            model_name='portfoller',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male', max_length=6),
        ),
        migrations.AddField(
            model_name='portfoller',
            name='profile_picture',
            field=models.ImageField(default='generic_user.png', upload_to=portfolio.models.profile_picture_path),
        ),
        migrations.AlterField(
            model_name='portfoller',
            name='career',
            field=models.CharField(choices=[('Developer', 'Developer'), ('Artist', 'Artist'), ('Writer', 'Writer')], max_length=20),
        ),
        migrations.AlterField(
            model_name='portfoller',
            name='contact_number',
            field=models.IntegerField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='portfoller',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.CreateModel(
            name='ProjectImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(null=True, upload_to=portfolio.models.project_images_path)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.project')),
            ],
        ),
    ]
