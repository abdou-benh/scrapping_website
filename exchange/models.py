from django.db import models

class ExchangeRate(models.Model):
    date = models.DateField()
    usd = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    eur = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"{self.date} - USD: {self.usd}, EUR: {self.eur}"

