# Generated by Django 3.1 on 2020-09-16 03:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog_site', '0003_changeemailcodes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changeemailcodes',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
