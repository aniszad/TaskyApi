# Generated by Django 5.0 on 2024-01-02 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_rename_project_id_project_projectid'),
        ('tasks', '0005_delete_task'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Project',
        ),
    ]