from django.db import models
import datetime

# Create your models here.
class Keyword(models.Model):
    keyword_text = models.CharField(max_length=255)

class Trend(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    search_period = models.CharField(max_length=50)
    result_count = models.IntegerField(default=0)
    search_date = models.DateTimeField(auto_now_add=True)