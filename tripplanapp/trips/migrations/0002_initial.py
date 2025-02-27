# Generated by Django 5.1.6 on 2025-02-27 21:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('apiposts', '0002_initial'),
        ('trips', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='tripmodel',
            name='leader',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trip', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tripmodel',
            name='roade_locations',
            field=models.ManyToManyField(related_name='trip', to='apiposts.triplocationmodel'),
        ),
    ]
