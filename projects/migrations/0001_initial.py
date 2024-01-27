# Generated by Django 5.0 on 2023-12-22 23:09

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('project_ID', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=99)),
                ('description', models.CharField(max_length=500)),
                ('priority', models.CharField(max_length=20)),
                ('status', models.CharField(default='Ongoing', max_length=10)),
                ('start_date', models.DateField(default=datetime.date(2023, 1, 1))),
                ('end_date', models.DateField(default=datetime.date(2023, 12, 12))),
                ('color', models.CharField(default='#FED36A', max_length=100)),
                ('members', models.ManyToManyField(related_name='projects', to=settings.AUTH_USER_MODEL)),
                ('ownerId', models.ForeignKey(db_column='owner_id', on_delete=django.db.models.deletion.CASCADE, related_name='owned_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'projects',
            },
        ),
    ]