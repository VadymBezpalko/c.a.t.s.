# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


# Create your models here.

class StockData(models.Model):
    symbol = models.CharField(max_length=50, default='')
    date = models.CharField(max_length=50, default='')
    open = models.CharField(max_length=50, default='')
    min = models.CharField(max_length=50, default='')
    max = models.CharField(max_length=50, default='')
    close = models.CharField(max_length=50, default='')
    change = models.CharField(max_length=50, default='')
    value = models.CharField(max_length=50, default='')
