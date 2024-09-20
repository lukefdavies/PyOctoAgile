import datetime
import logging
import subprocess
import schedule
import time

# Configurable temperatures
HIGH_TEMPERATURE = 21
LOW_TEMPERATURE = 16

HIGH_TEMPERATURE_COMMAND = ['python3', 'thermostat_control.py', str(HIGH_TEMPERATURE)]
LOW_TEMPERATURE_COMMAND = ['python3', 'thermostat_control.py', str(LOW_TEMPERATURE)]
GET_PRICES_COMMAND = ['python3', 'return_agile_periods.py']

# Set up logging
logging.basicConfig(filename='pyoctoagile.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def read_periods():
    """Read sorted periods from the file."""
    logging.debug("Reading heating periods from file.")
    with open('heating_periods.txt', 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    periods = []
    for line in lines:
        try:
            # Parse start and end times from the line
            start_str, end_str = line.split(' - ')
            start_time = datetime.datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.datetime.strptime(end_str, '%H:%M').time()

            periods.append((start_time, end_time))
            logging.debug(f"Loaded period: {start_str} to {end_str}")
        except ValueError as e:
            logging.error(f"Error processing line: {line}. Error: {e}")

    return periods

def schedule_temperatures():
    """Schedule temperature changes based on the sorted periods."""
    logging.info("Starting to schedule temperature changes.")
    now = datetime.datetime.now().time()
    periods = read_periods()

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
        for period_start, period_end in periods:
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
    """Reload the heating periods from the file and reschedule temperatures."""
    logging.info("Reloading heating periods from file.")
    schedule_temperatures()  # Reschedule based on the updated periods

def return_prices():
    """Get the prices for a new day."""
    logging.info("Getting prices for new day.")
    execute_command(GET_PRICES_COMMAND)

if __name__ == "__main__":
    # Initial scheduling
    logging.info("Starting the OctoPyAgile temperature scheduler.")
    schedule_temperatures()

    # Schedule daily reloading of periods and prices
    schedule.every().day.at("00:01").do(return_prices)
    schedule.every().day.at("00:02").do(reload_periods)

    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)
