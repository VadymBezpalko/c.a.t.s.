# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


# Create your models here.

class StockData(models.Model):
    symbol = models.CharField(max_length=50, default='')
    date = models.DateField()
    open = models.FloatField()
    min = models.FloatField()
    max = models.FloatField()
    close = models.FloatField()
    change = models.FloatField()
    value = models.FloatField()
