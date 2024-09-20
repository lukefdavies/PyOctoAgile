# PyOctoAgile

PyOctoAgile is a Python-based tool designed to automate thermostat control based on energy pricing data from Octopus Energy’s Agile tariff. The system schedules heating to maximize cost savings by adjusting temperatures during lower-priced periods.

## Features

- **Fetch Agile Tariff Prices**: Retrieves half-hourly electricity prices for the day and identifies periods that fall below a specified percentile.
- **Thermostat Control**: Automatically sets the temperature for multiple thermostats based on the retrieved pricing data, targeting high temperatures during cheaper periods.
- **Automated Scheduling**: Uses `schedule` to automate daily tasks such as fetching new price data and re-scheduling thermostat settings.

## Structure

### Main Components:
1. **`PyOctoAgile.py`**: The main script that handles scheduling, executing commands for thermostat control, and retrieving energy prices.
   - Reads periods below the pricing percentile from `heating_periods.txt`.
   - Schedules temperature changes for thermostats based on price data.
   - Daily tasks for retrieving prices and reloading periods are automated.
   
2. **`thermostat_control.py`**: Controls the thermostat by interacting with Home Assistant’s API.
   - Sets the temperature for defined thermostats based on a target temperature passed as a command-line argument.

3. **`return_agile_periods.py`**: Fetches daily electricity pricing data from the Octopus Energy Agile tariff and identifies periods where the price is below a given percentile.
   - Saves time intervals below the pricing threshold to `heating_periods.txt`.

## Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:yourusername/PyOctoAgile.git
   ```

2. **Install dependencies**:
   Ensure you have `requests`, `numpy`, `pytz`, and `schedule` installed. You can install them with:
   ```bash
   pip install requests numpy pytz schedule
   ```

3. **Set up Home Assistant**:  
   - Replace `HOME_ASSISTANT_URL` and `API_TOKEN` in `thermostat_control.py` with your Home Assistant instance and long-lived access token.

4. **Set up Octopus Energy API**:
   - In `return_agile_periods.py`, replace `PRODUCT_CODE` and `TARIFF_CODE` with your relevant Octopus Energy product and tariff codes.

## Usage

### 1. Running the Service
The main script `PyOctoAgile.py` handles scheduling and controlling thermostats. You can run it manually or use a systemd service for continuous execution.

### 2. Systemd Service (Optional)
To run PyOctoAgile as a systemd service:
1. Place the service file in `/etc/systemd/system`:
   ```bash
   sudo cp Program/systemd/pyoctoagile.service /etc/systemd/system/pyoctoagile.service
   ```
2. Reload systemd and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start pyoctoagile.service
   sudo systemctl enable pyoctoagile.service
   ```

### 3. Fetch New Prices and Reschedule
The system automatically fetches new prices and updates the thermostat schedule at 00:01 each day. To manually trigger this process, you can run:
   ```bash
   python3 return_agile_periods.py
   python3 PyOctoAgile.py
   ```

## Configuration

- **Thermostat Configuration**:
   - Update `ENTITY_IDS` in `thermostat_control.py` to match your Home Assistant climate entities.
   - Adjust the `HIGH_TEMPERATURE` and `LOW_TEMPERATURE` in `PyOctoAgile.py` to set your preferred temperature ranges.

- **Pricing Percentile**:
   - The `PERCENTILE_THRESHOLD` in `return_agile_periods.py` controls the pricing threshold. Lower values increase savings but may reduce comfort. Adjust to your preference.

## Logs

Logs are written to `pyoctoagile.log` by default. You can review them to debug any issues or monitor system behavior.

## Contributions

Feel free to open issues or submit pull requests to improve the project!

## License

This project is licensed under the MIT License.
