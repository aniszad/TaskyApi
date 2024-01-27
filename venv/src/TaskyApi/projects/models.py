from django.db import models

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length = 99)
    description = models.CharField(max_length = 500)
    priority = models.CharField(max_length=6)
    owner_id = models.IntegerField()
