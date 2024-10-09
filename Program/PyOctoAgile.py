import datetime
import logging
import subprocess
import schedule
import time
from return_agile_periods import get_heating_periods  # Import the function
import os

# Configurable temperatures
HIGH_TEMPERATURE = 20.5
LOW_TEMPERATURE = 15

home_directory = os.path.expanduser("~")
thermostat_script_path = os.path.join(home_directory, 'PyOctoAgile/Program/thermostat_control.py')

HIGH_TEMPERATURE_COMMAND = ['python3', thermostat_script_path, str(HIGH_TEMPERATURE)]
LOW_TEMPERATURE_COMMAND = ['python3', thermostat_script_path, str(LOW_TEMPERATURE)]

# Set up logging
log_file = os.path.expanduser('~/PyOctoAgile/Program/pyoctoagile.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Logging initialized.")

def schedule_temperatures():
    """Schedule temperature changes based on the sorted periods."""
    logging.info("Starting to schedule temperature changes.")

    # Get the heating periods and the percentile threshold
    periods, percentile_threshold = get_heating_periods()

    # Log the calculated 50th percentile price
    logging.info(f"Calculated 50th Percentile Threshold: {percentile_threshold:.2f}p")

    # Clear all temperature-related schedules but preserve the reload task
    schedule.clear('temperature')

    logging.info("Cleared all previous temperature schedules.")
    
    #Ensure the daily reload of heating perids remains scheduled (paranoia)
    schedule.every().day.at("00:01").do(reload_periods)
    logging.info(f"Scheduling daily reload of heating periods and prices at {reload_time}.")

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
                    schedule.every().day.at(f"{start_interval.strftime('%H:%M')}").do(execute_command, HIGH_TEMPERATURE_COMMAND).tag('temperature')
                    logging.info(f"Scheduled high temperature at {start_interval.strftime('%H:%M')}")
                    last_scheduled_temp = 'high'
                scheduled = True
                break

        if not scheduled and last_scheduled_temp != 'low':
            # Schedule low temperature if not within any high temperature period and last scheduled was not low
            schedule.every().day.at(f"{start_interval.strftime('%H:%M')}").do(execute_command, LOW_TEMPERATURE_COMMAND).tag('temperature')
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

def check_missed_schedule():
    """Check if the current time is within a heating period and set the temperature immediately."""
    now = datetime.datetime.now().time()

    # Get the heating periods
    periods, _ = get_heating_periods()

    for period_start_str, period_end_str in periods:
        period_start = datetime.datetime.strptime(period_start_str, '%H:%M').time()
        period_end = datetime.datetime.strptime(period_end_str, '%H:%M').time()

        if period_start <= now < period_end:
            logging.info(f"Current time {now} is within a high temperature period ({period_start_str} - {period_end_str}). Setting high temperature.")
            execute_command(HIGH_TEMPERATURE_COMMAND)
            return

    # If no high temperature period is found, set low temperature
    logging.info(f"Current time {now} is not within any high temperature period. Setting low temperature.")
    execute_command(LOW_TEMPERATURE_COMMAND)

if __name__ == "__main__":
    # Initial scheduling
    logging.info("Starting the OctoPyAgile temperature scheduler.")
    
    # Check if the current time is within a heating period and adjust the temperature immediately
    check_missed_schedule()

    # Schedule temperature changes
    schedule_temperatures()

    # Schedule daily reloading of periods and prices
    schedule.every().day.at("00:01").do(reload_periods)
    logging.info(f"Scheduling daily reload of heating periods and prices at {reload_time}.")

    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)
