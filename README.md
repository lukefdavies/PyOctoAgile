![Logo](Program/assets/icon.png)
# PyOctoAgile

PyOctoAgile is a Python-based tool designed to automate thermostat control based on energy pricing data from Octopus Energy’s Agile tariff. The system schedules heating to maximize cost savings by adjusting temperatures during lower-priced periods.

## Features

- **Fetch Agile Tariff Prices**: Retrieves half-hourly electricity prices for the day and identifies periods that fall below a specified percentile.
- **Thermostat Control**: Automatically sets the temperature for multiple thermostats based on the retrieved pricing data, targeting high temperatures during cheaper periods. Requires integration with Home Assistant, which acts as the hub for communicating with connected thermostats.
- **Automated Scheduling**: Uses '''schedule''' to automate daily tasks such as fetching new price data and re-scheduling thermostat settings, ensuring optimal heating schedules based on real-time price data.
- **Home Assistant Dependency**: Fully integrates with Home Assistant to control various compatible smart thermostats. This integration is essential for the functionality of PyOctoAgile and requires that users have an active Home Assistant setup.

## Requirements

- **Home Assistant**: You must have a Home Assistant instance running with network access to the same environment where PyOctoAgile is deployed.
- **Connected Thermostats**: At least one compatible smart thermostat must be connected and configured within your Home Assistant setup.
- **Octopus Energy Account**: An active account with Octopus Energy and subscription to the Agile tariff to access the dynamic pricing data.

## Planned Improvements

- **Configuration Script (`config.py`)**: Introduce a configuration script (`config.py`) that allows users to easily modify key variables (such as tariff codes, thermostat IDs, temperatures, etc.) with validation checks. This will store settings in a centralized `config.json` file, simplifying configuration management.
- **Move to `config.json` for Variables**: Shift to using a `config.json` file for storing all configurable variables (tariffs, thermostat settings, schedules, etc.), allowing for easier updates and integration with the planned Web Interface and future APIs.
- **Web Interface**: Implement a web-based configuration interface to allow users to modify settings easily without direct interaction with the backend code.
- **Advanced Analytics**: Integrate advanced analytics to track heating performance and energy savings over time.
- **Enhanced Error Handling**: Develop robust error handling and logging capabilities to ensure the system's reliability and ease troubleshooting.
- **User Customization**: Enhance user settings to include custom schedules and temperature settings, allowing for greater personalization.
- **Dynamic Temperature Adjustment**: Monitor climate ID data to adjust the percentile of timeslots used for heating, enhancing efficiency and comfort based on real-time temperature performance.
- **Occupancy-Based Control**: Utilize home network data to determine occupancy, adjusting heating operations based on the presence of registered smartphones or occupancy sensors.
- **Support for Multiple Energy Providers**: Extend compatibility to include additional energy providers who offer APIs and flexible tariffs, broadening the applicability of PyOctoAgile across different regions and market conditions.

## Structure

### Main Components:
1. **`PyOctoAgile.py`**: The main script that handles scheduling, executing commands for thermostat control, and retrieving energy prices.
   - Reads periods below the pricing percentile directly from '''return_agile_periods.py'''.
   - Schedules temperature changes for thermostats based on price data.
   - Daily tasks for retrieving prices and reloading periods are automated.
   
2. **`thermostat_control.py`**: Controls the thermostat by interacting with Home Assistant’s API.
   - Sets the temperature for defined thermostats based on a target temperature passed as a command-line argument.

3. **`return_agile_periods.py`**: Fetches daily electricity pricing data from the Octopus Energy Agile tariff and identifies periods where the price is below a given percentile.

## Installation

1. **Clone the repository**:
   '''git clone https://github.com/lukefdavies/PyOctoAgile.git'''

2. **Install dependencies**:
   Ensure you have the following Python packages installed:
   
   - `requests`: For making HTTP requests to the Octopus Energy and Home Assistant APIs.
   - `numpy`: For calculating percentiles from price data.
   - `pytz`: For handling time zone conversions (BST/GMT).
   - `schedule`: For managing the scheduling of thermostat changes and price fetching.
   - `logging`: For logging activity and debugging (usually part of the standard Python library).
   - `os`: For managing environment variables (also part of the standard Python library).

You can install the external dependencies with:

```pip install requests numpy pytz schedule```

### 3. Set up Home Assistant

You will need to configure the Home Assistant URL and token in `thermostat_control.py` to communicate with your Home Assistant instance.

#### Option 1: Replace Directly in the Script
1. '''HOME_ASSISTANT_URL''' and '''API_TOKEN''' in `thermostat_control.py` with your actual Home Assistant instance URL and long-lived access token.
   - **Example**:
     '''
     HOME_ASSISTANT_URL = "http://your-home-assistant.local:8123"
     API_TOKEN = "your-long-lived-access-token-here"
     '''

#### Option 2: Use Environment Variables for Better Security

A more secure approach is to avoid hardcoding the access token in your script. Instead, you can store it as an environment variable. Here's how you can do that:

1. **Add `HOME_ASSISTANT_TOKEN` to your environment variables**:
   - **Linux/macOS**:
     1. Open a terminal.
     2. Add the token to your `.bashrc`, `.zshrc`, or similar shell config file by running:
        '''echo 'export HOME_ASSISTANT_TOKEN="your-long-lived-access-token-here"' >> ~/.bashrc'''
     3. Reload the shell configuration by running:
        '''source ~/.bashrc'''

2. **Modify `thermostat_control.py` to use the environment variable**:
   - Instead of hardcoding the token in your script, use Python's `os` module to retrieve the token from the environment:
     '''
     import os

     HOME_ASSISTANT_URL = "http://your-home-assistant.local:8123"
     API_TOKEN = os.getenv('HOME_ASSISTANT_TOKEN')

     if not API_TOKEN:
         raise ValueError("Error: HOME_ASSISTANT_TOKEN not set in environment variables.")
     '''

3. **Run your script**:
   Once the environment variable is set, you can run your script as normal, and it will automatically pull the `HOME_ASSISTANT_TOKEN` from your environment.

4. **Set up Octopus Energy API**:
   - In `return_agile_periods.py`, replace `PRODUCT_CODE` and `TARIFF_CODE` with your relevant Octopus Energy product and tariff codes.

## Usage

### 1. Running the Service
The main script `PyOctoAgile.py` handles scheduling and controlling thermostats. You can run it manually or use a systemd service for continuous execution.

### 2. Systemd Service (Optional)
To run PyOctoAgile as a systemd service:
1. Place the service file in `/etc/systemd/system`:
   '''sudo cp Program/systemd/pyoctoagile.service /etc/systemd/system/pyoctoagile.service'''
2. Reload systemd and start the service:
   '''
   sudo systemctl daemon-reload
   sudo systemctl start pyoctoagile.service
   sudo systemctl enable pyoctoagile.service
   '''

### 3. Fetch New Prices and Reschedule
The system automatically fetches new prices and updates the thermostat schedule at 00:01 each day. To manually trigger this process, you can run:
   '''python3 return_agile_periods.py'''
   '''python3 PyOctoAgile.py'''

## Configuration

- **Thermostat Configuration**:
   - Update '''ENTITY_IDS''' in `thermostat_control.py` to match your Home Assistant climate entities.
   - Adjust the `HIGH_TEMPERATURE` and `LOW_TEMPERATURE` in `PyOctoAgile.py` to set your preferred temperature ranges.

- **Pricing Percentile**:
   - The `PERCENTILE_THRESHOLD` in `return_agile_periods.py` controls the pricing threshold. Lower values increase savings but may reduce comfort. Adjust to your preference.

## Logs

Logs are written to `'''~/PyOctoAgile/Program/pyoctoagile.log'''` by default. You can review them to debug any issues or monitor system behavior.

## Contributions

Feel free to open issues or submit pull requests to improve the project!

## License

This project is licensed under the MIT License.
