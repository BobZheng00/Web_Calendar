# Generated by Django 5.0.1 on 2024-01-15 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_channel', '0005_userevents_is_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='userevents',
            name='hex_color',
            field=models.CharField(default='#000000', max_length=7),
        ),
    ]
