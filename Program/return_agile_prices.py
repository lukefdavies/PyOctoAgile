import requests
from datetime import datetime, timedelta
import numpy as np
import pytz

# Replace with your actual product and tariff codes
PRODUCT_CODE = "AGILE-23-12-06"
TARIFF_CODE = "E-1R-AGILE-23-12-06-L"
octopus_api_url = f"https://api.octopus.energy/v1/products/{PRODUCT_CODE}/electricity-tariffs/{TARIFF_CODE}/standard-unit-rates/"

# Configurable percentile
PERCENTILE_THRESHOLD = 50  # Change this to adjust the percentile

# Timezone setup
utc = pytz.utc
local_tz = pytz.timezone("Europe/London")

def convert_to_local_time(utc_time_str):
    # Convert string to UTC datetime object
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=pytz.utc)  # Assign the correct timezone

    # Convert to local time (BST or GMT depending on date)
    local_time = utc_time.astimezone(local_tz)
    return local_time

def get_daily_prices():
    # Fetch pricing data from Octopus API
    response = requests.get(octopus_api_url)
    prices = response.json()

    # Filter for prices for today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz)
    today_end = today_start + timedelta(hours=23, minutes=59)

    # Collect all prices for today
    all_prices = [price for price in prices['results']
                  if today_start <= convert_to_local_time(price['valid_from']) <= today_end]

    return all_prices

def filter_daytime_prices(prices):
    daytime_prices = []
    for price in prices:
        start_time = convert_to_local_time(price['valid_from'])
        hour = start_time.hour

        # Keep only morning and daytime periods
        if 5 <= hour < 22:  # Morning and Daytime (5am to 10pm)
            daytime_prices.append(price)

    return daytime_prices

def calculate_percentile(prices, percentile):
    # Extract price values and calculate the given percentile
    values = [price['value_inc_vat'] for price in prices]
    return np.percentile(values, percentile)

def find_below_percentile_prices(prices, percentile):
    threshold = calculate_percentile(prices, percentile)
    below_percentile = [price for price in prices if price['value_inc_vat'] < threshold]
    return below_percentile

# Main logic
prices = get_daily_prices()
daytime_prices = filter_daytime_prices(prices)
threshold_percentile = PERCENTILE_THRESHOLD
below_percentile_prices = find_below_percentile_prices(daytime_prices, threshold_percentile)

# Sort periods by time
sorted_below_percentile_prices = sorted(below_percentile_prices, key=lambda x: convert_to_local_time(x['valid_from']))

# Save results to a file with just the time periods
with open('heating_periods.txt', 'w') as f:
    for price in sorted_below_percentile_prices:
        start_time = convert_to_local_time(price['valid_from'])
        end_time = start_time + timedelta(minutes=30)
        f.write(f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n")

print(f"Periods below {threshold_percentile}th percentile price saved to 'heating_periods.txt'.")
