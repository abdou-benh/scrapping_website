from django.shortcuts import render
from django.http import HttpResponse
from .models import ExchangeRate
from bs4 import BeautifulSoup
import requests
import urllib3
from datetime import datetime
from django.http import HttpResponse

from django.shortcuts import render
from exchange.models import ExchangeRate


def index(request):
    # Get the number of records from the GET request, default to 5
    num_records = request.GET.get('num_records', 5)
    
    try:
        num_records = int(num_records)
        if num_records < 1:
            num_records = 5  # Default value if invalid
    except ValueError:
        num_records = 5  # Default value if invalid input
    
    # Fetch the specified number of most recent records
    if num_records > 10:
        message = "You can only view up to 10 records at a time."
        recent_rates = ExchangeRate.objects.order_by('-date')[:10]
    else:
        message = ""
        recent_rates = ExchangeRate.objects.order_by('-date')[:num_records]
    
    return render(request, 'index.html', {'exchange_rates': recent_rates, 'message': message})

def fetch_exchange_rates(request):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = "https://www.bank-of-algeria.dz/taux-de-change-journalier/"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        return HttpResponse(f"Request failed: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    div = soup.find('div', id='organizTable')
    if not div:
        return HttpResponse("Could not find the div with id 'organizTable'")

    tables = div.find_all('table')
    exchange_rates = []

    for idx, table in enumerate(tables):
        thead = table.find('thead')
        tbody = table.find('tbody')

        if thead:
            ths = thead.find_all('th')
            if len(ths) > 1:
                date_header = ths[1].text.strip()
            elif len(ths) == 1:
                date_header = ths[0].text.strip()
            else:
                date_header = 'Unknown Date'
        else:
            continue

        if tbody:
            rows = tbody.find_all('tr')
            if idx == 0:
                rates = {}
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue
                    currency = cells[0].text.strip()
                    rate = cells[1].text.strip()
                    if currency in ['USD', 'EUR']:
                        rates[currency] = rate
                if rates:
                    exchange_rates.append((date_header, rates.get('USD'), rates.get('EUR')))
            else:
                if len(rows) >= 2:
                    usd_rate = rows[0].find_all('td')[0].text.strip()
                    eur_rate = rows[1].find_all('td')[0].text.strip()
                    exchange_rates.append((date_header, usd_rate, eur_rate))

    if exchange_rates:
        for date_str, usd, eur in exchange_rates:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
            ExchangeRate.objects.create(date=date_obj, usd=usd, eur=eur)
        return HttpResponse("Exchange rates successfully saved to the database.")
    else:
        return HttpResponse("No exchange rates found.")
