# Generated by Django 5.2 on 2025-06-08 06:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0006_remove_post_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='board.thread'),
        ),
    ]
