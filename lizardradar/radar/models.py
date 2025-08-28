from django.db import models

# Create your models here.

class Warning(models.Model):
    nws_id = models.CharField(max_length=255, unique=True)
    event = models.CharField(max_length=255)
    headline = models.TextField()
    area_desc = models.TextField()
    effective = models.DateTimeField()
    expires = models.DateTimeField(null=True, blank=True)
    geojson = models.JSONField()  # Store the entire GeoJSON here

    def __str__(self):
        return f"{self.event} ({self.area_desc})"
