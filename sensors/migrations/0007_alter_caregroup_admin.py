# Generated by Django 3.2.8 on 2021-11-10 19:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0006_auto_20211110_1938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caregroup',
            name='admin',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='caregroup_admin', to=settings.AUTH_USER_MODEL),
        ),
    ]
