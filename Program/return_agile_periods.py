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
    """Convert a UTC time string to local time (GMT/BST)."""
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=utc)
    local_time = utc_time.astimezone(local_tz)
    return local_time

def get_daily_prices():
    """Fetch pricing data from Octopus API and filter for today's prices."""
    response = requests.get(octopus_api_url)
    prices = response.json()

    today_start = datetime.now(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(hours=23, minutes=59)

    all_prices = [price for price in prices['results']
                  if today_start <= convert_to_local_time(price['valid_from']) <= today_end]

    print(f"\nAll Prices for Today (UTC): {[convert_to_local_time(p['valid_from']).strftime('%H:%M') + ' - ' + str(p['value_inc_vat']) for p in all_prices]}")

    return all_prices

def filter_daytime_prices(prices):
    """Filter prices to only include morning and daytime periods (5am to 10pm)."""
    daytime_prices = []
    for price in prices:
        start_time = convert_to_local_time(price['valid_from'])
        if 5 <= start_time.hour < 22:
            daytime_prices.append(price)

    print(f"\nDaytime Prices (5am to 10pm): {[convert_to_local_time(p['valid_from']).strftime('%H:%M') + ' - ' + str(p['value_inc_vat']) for p in daytime_prices]}")
    return daytime_prices

def calculate_percentile(prices, percentile):
    """Calculate the given percentile for the list of prices."""
    values = [price['value_inc_vat'] for price in prices]
    result = np.percentile(values, percentile)
    print(f"\nCalculated {percentile}th Percentile Threshold: {result:.2f}p")
    return result

def find_below_percentile_prices(prices, percentile):
    """Find prices below the given percentile."""
    threshold = calculate_percentile(prices, percentile)
    below_percentile = [price for price in prices if price['value_inc_vat'] < threshold]

    print(f"\nPrices Below {percentile}th Percentile: {[convert_to_local_time(p['valid_from']).strftime('%H:%M') + ' - ' + str(p['value_inc_vat']) for p in below_percentile]} + 'p'")
    return below_percentile

def get_heating_periods():
    """Main function to get sorted periods below the percentile."""
    prices = get_daily_prices()
    daytime_prices = filter_daytime_prices(prices)
    percentile_threshold = calculate_percentile(daytime_prices, PERCENTILE_THRESHOLD)
    below_percentile_prices = find_below_percentile_prices(daytime_prices, PERCENTILE_THRESHOLD)
    
    # Sort periods by time
    sorted_periods = sorted(below_percentile_prices, key=lambda x: convert_to_local_time(x['valid_from']))
    
    # Return start and end times for each period, and the threshold
    periods = [(convert_to_local_time(p['valid_from']).strftime('%H:%M'),
                (convert_to_local_time(p['valid_from']) + timedelta(minutes=30)).strftime('%H:%M'))
               for p in sorted_periods]
    
    return periods, percentile_threshold


if __name__ == "__main__":
    get_heating_periods()
