# Generated by Django 4.0.6 on 2024-01-04 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_channel', '0004_follower'),
    ]

    operations = [
        migrations.AddField(
            model_name='userevents',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]