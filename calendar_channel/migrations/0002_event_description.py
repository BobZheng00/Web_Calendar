# Generated by Django 4.0.6 on 2022-08-27 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_channel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
