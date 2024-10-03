import datetime
import logging
import subprocess
import schedule
import time
from return_agile_prices import get_heating_periods  # Import the function

# Configurable temperatures
HIGH_TEMPERATURE = 20.5
LOW_TEMPERATURE = 15

HIGH_TEMPERATURE_COMMAND = ['python3', 'thermostat_control.py', str(HIGH_TEMPERATURE)]
LOW_TEMPERATURE_COMMAND = ['python3', 'thermostat_control.py', str(LOW_TEMPERATURE)]

# Set up logging
logging.basicConfig(filename='pyoctoagile.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def schedule_temperatures():
    """Schedule temperature changes based on the sorted periods."""
    logging.info("Starting to schedule temperature changes.")
    now = datetime.datetime.now().time()

    # Get the heating periods directly from return_agile_prices
    periods = get_heating_periods()

    # Clear all existing schedules
    schedule.clear()
    logging.info("Cleared all previous schedules.")

    # Convert periods into 30-minute intervals for scheduling
    intervals = []
    for hour in range(24):
        for minute in [0, 30]:
            start_interval = datetime.time(hour, minute)
            intervals.append(start_interval)

    last_scheduled_temp = None  # Track the last scheduled temperature

    for start_interval in intervals:
        scheduled = False
        for period_start_str, period_end_str in periods:
            period_start = datetime.datetime.strptime(period_start_str, '%H:%M').time()
            period_end = datetime.datetime.strptime(period_end_str, '%H:%M').time()

            if period_start <= start_interval < period_end:
                # If within a high temperature period and last scheduled was not high, schedule high temperature
                if last_scheduled_temp != 'high':
                    schedule.every().day.at(f"{start_interval.strftime('%H:%M')}").do(execute_command, HIGH_TEMPERATURE_COMMAND)
                    logging.info(f"Scheduled high temperature at {start_interval.strftime('%H:%M')}")
                    last_scheduled_temp = 'high'
                scheduled = True
                break

        if not scheduled and last_scheduled_temp != 'low':
            # Schedule low temperature if not within any high temperature period and last scheduled was not low
            schedule.every().day.at(f"{start_interval.strftime('%H:%M')}").do(execute_command, LOW_TEMPERATURE_COMMAND)
            logging.info(f"Scheduled low temperature at {start_interval.strftime('%H:%M')}")
            last_scheduled_temp = 'low'

def execute_command(command):
    """Execute a command and log the event."""
    subprocess.run(command)
    logging.info(f"Executed command: {' '.join(command)}")

def reload_periods():
    """Reload the heating periods and reschedule temperatures."""
    logging.info("Reloading heating periods.")
    schedule_temperatures()  # Reschedule based on the updated periods

if __name__ == "__main__":
    # Initial scheduling
    logging.info("Starting the OctoPyAgile temperature scheduler.")
    schedule_temperatures()

    # Schedule daily reloading of periods and prices
    schedule.every().day.at("00:01").do(reload_periods)

    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)
