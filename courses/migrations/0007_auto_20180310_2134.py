# Generated by Django 2.0.2 on 2018-03-10 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_auto_20180310_1928'),
    ]

    operations = [
        migrations.RenameField(
            model_name='questionforum',
            old_name='topic',
            new_name='lecture',
        ),
    ]
