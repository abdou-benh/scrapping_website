from django.core.management.base import BaseCommand  
from exchange.models import ExchangeRate  
from bs4 import BeautifulSoup  
import requests  
import urllib3  
from datetime import datetime  

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Disable warnings about insecure requests

class Command(BaseCommand):  
    help = 'Fetch exchange rates and save them to the database'  

    def handle(self, *args, **kwargs):  
        url = "https://www.bank-of-algeria.dz/taux-de-change-journalier/"  # URL to fetch exchange rates from
        try:
            response = requests.get(url, verify=False)  # Make an HTTP GET request to the URL
            response.raise_for_status()  # Raise an error if the request was unsuccessful
        except requests.RequestException as e:
            self.stdout.write(f"Request failed: {e}")  
            return  

        soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content of the response
        div = soup.find('div', id='organizTable')  # Find the <div> element with the id 'organizTable'
        if not div:
            self.stdout.write("Could not find the div with id 'organizTable'")  
            return  

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
                            continue  # Skip rows with fewer than two <td> elements
                        currency = cells[0].text.strip()  # Extract the currency code from the first <td>
                        rate = cells[1].text.strip()  # Extract the exchange rate from the second <td>
                        if currency in ['USD', 'EUR']:
                            rates[currency] = rate  # Add the rate to the dictionary if the currency is USD or EUR
                    if rates:
                        exchange_rates.append((date_header, rates.get('USD'), rates.get('EUR')))  
                else:
                    if len(rows) >= 2:
                        usd_rate = rows[0].find_all('td')[0].text.strip()  # Extract the USD rate from the first row
                        eur_rate = rows[1].find_all('td')[0].text.strip()  # Extract the EUR rate from the second row
                        exchange_rates.append((date_header, usd_rate, eur_rate))  # Add the rates to the list

        if exchange_rates:
            # Process the exchange rates
            for date_str, usd, eur in exchange_rates:  # Iterate over each exchange rate entry
                try:
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()  # Parse the date string into a date object
                except ValueError:
                    self.stdout.write(f"Date format error: {date_str}")  
                    continue  

                
                existing_rate = ExchangeRate.objects.filter(date=date_obj).first()  # Check if a record with the same date exists
                if existing_rate:
                    existing_rate.usd = usd  
                    existing_rate.eur = eur  
                    existing_rate.save()  
                else:
                    
                    ExchangeRate.objects.create(date=date_obj, usd=usd, eur=eur)  # Create a new exchange rate record

            self.stdout.write("Exchange rates successfully processed.")  
        else:
            self.stdout.write("No exchange rates found.")  

