# Generated by Django 3.1 on 2020-09-03 05:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog_site', '0007_auto_20200903_0515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog_post_comments',
            name='blog_post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='blog_site.blog_post'),
        ),
    ]