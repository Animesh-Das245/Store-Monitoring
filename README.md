# Store Monitoring System

## Overview

This Store Monitoring System is designed to track and report the uptime and downtime of various stores based on their operational status and business hours. It uses data from multiple sources, analyzes it, and generates reports to provide insights into store activities.

## Features

- **Data Import**: Imports data from CSV files into an SQLite database for easy manipulation and querying.
- **Timezone Handling**: Converts local business hours into UTC for accurate comparison with UTC-based store status timestamps.
- **Report Generation**: Calculates the uptime and downtime of stores over specified periods (last hour, last day, last week) within their business hours.

## Data Sources and Directory Structure

The system uses three primary data sources, which are expected to be located in the `static` folder:

- **Store Status (`store_status.csv`)**: Contains records of store activities with timestamps.
- **Business Hours (`menu_hours.csv`)**: Business hours of stores.
- **Timezones (`timezones.csv`)**: Timezone information for each store.

### Directory Structure

- `static/`: Contains the CSV files used for importing data into the system.
- `reports/`: Where the system saves generated reports. Ensure this folder exists before running the application.

## Setup and Installation


1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

3. **Initialize Database**:
  ```bash
   python initialize_db.py
  ```
   
## Running the Application

1. **Start the Flask Server**:
```bash
python run.py

```

2. **Access the Application**:
- The application will be available at `http://127.0.0.1:5000`.

## API Endpoints

- **Trigger Report Generation**:
- Endpoint: `/trigger_report`
- Method: `GET`
- Description: Triggers the generation of a new report.
- Returns: `report_id`

- **Get Report**:
- Endpoint: `/get_report/<report_id>`
- Method: `GET`
- Description: Retrieves the status or the generated report based on the provided `report_id`.

## Report Format

The generated reports include the following fields:

- `store_id`
- `uptime_last_hour` (in minutes)
- `uptime_last_day` (in hours)
- `uptime_last_week` (in hours)
- `downtime_last_hour` (in minutes)
- `downtime_last_day` (in hours)
- `downtime_last_week` (in hours)




