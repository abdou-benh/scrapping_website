from django.contrib import admin
from .models import ExchangeRate

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('date', 'usd', 'eur')
    list_filter = ('date',)
    search_fields = ('date',)
