# Generated by Django 5.0 on 2023-12-24 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_alter_project_ownerid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='project_ID',
            new_name='projectId',
        ),
    ]
