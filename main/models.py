# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


# Create your models here.

class StockData(models.Model):
    symbol = models.CharField(max_length=50, default='')
    date = models.DateField(blank=True)
    open = models.DecimalField(blank=False, max_digits=10, decimal_places=6)
    min = models.DecimalField(blank=False, max_digits=10, decimal_places=6)
    max = models.DecimalField(blank=False, max_digits=10, decimal_places=6)
    close = models.DecimalField(blank=False, max_digits=10, decimal_places=6)
    change = models.CharField(max_length=50, blank=True)
    value = models.DecimalField(blank=False, max_digits=10, decimal_places=6)
