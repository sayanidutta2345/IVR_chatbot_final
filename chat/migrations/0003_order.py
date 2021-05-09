# Generated by Django 3.2 on 2021-04-28 07:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20210426_1823'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('orderid', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('details', models.TextField()),
                ('status', models.CharField(max_length=10)),
                ('date_ordered', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]