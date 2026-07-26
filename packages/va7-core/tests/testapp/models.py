from django.db import models

from va7.core.models import BaseModel


class Article(BaseModel):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, default="")

    class Meta:
        app_label = "testapp"


class Tag(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "testapp"
