from django.db import models

# Create your models here.
from django.db import models


class APICache(models.Model):
    endpoint = models.CharField(max_length=255)
    params = models.TextField()
    data = models.JSONField()

    class Meta:
        unique_together = ('endpoint', 'params')

    def __str__(self):
        return f"{self.endpoint} - {self.params}"
