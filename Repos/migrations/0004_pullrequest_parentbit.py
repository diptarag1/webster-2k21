# Generated by Django 3.2.7 on 2021-12-26 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Repos', '0003_pullrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='pullrequest',
            name='parentBit',
            field=models.BooleanField(default=False),
        ),
    ]
