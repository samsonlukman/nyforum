# Generated by Django 5.2.2 on 2025-06-10 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumthread',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='forum/'),
        ),
    ]
