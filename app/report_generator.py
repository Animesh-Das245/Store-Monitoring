import pandas as pd
import pytz
from datetime import datetime, timedelta
from .database import get_db_connection

def safe_convert_to_utc(row, tz_column, time_column, default_tz='UTC', time_format='%H:%M:%S'):
    tz_str = row.get(tz_column) if pd.notna(row[tz_column]) else default_tz
    local_tz = pytz.timezone(tz_str)

    time_str = row.get(time_column, '00:00:00')
    if '.' in time_str:  # Handle fractional seconds
        time_str, _ = time_str.split('.', 1)
    local_time = datetime.strptime(time_str, time_format).time()

    utc_time = local_tz.localize(datetime.combine(datetime.today(), local_time)).astimezone(pytz.utc)
    return utc_time.time()

def calculate_uptime_downtime(store_status, business_hours, current_utc, days_ago):
    start_time = current_utc - timedelta(days=days_ago)
    end_time = current_utc
    relevant_status = store_status[(store_status['timestamp_utc'] >= start_time) & (store_status['timestamp_utc'] <= end_time)]
    uptime, downtime = 0, 0

    for single_day in (start_time + timedelta(n) for n in range(int(days_ago)+1)):
        day_of_week = single_day.weekday()
        daily_hours = business_hours[business_hours['day'] == day_of_week]

        if not daily_hours.empty:
            business_start_utc = datetime.combine(single_day, daily_hours.iloc[0]['start_time_utc'])
            business_end_utc = datetime.combine(single_day, daily_hours.iloc[0]['end_time_utc'])
            active_status = relevant_status[(relevant_status['timestamp_utc'] >= business_start_utc) & (relevant_status['timestamp_utc'] <= business_end_utc)]
            if not active_status.empty:
                active_hours = active_status['status'].value_counts()
                uptime += active_hours.get('active', 0)
                downtime += active_hours.get('inactive', 0)

    return uptime, downtime

def generate_report(report_id):
    conn = get_db_connection()

    store_status_df = pd.read_sql_query("SELECT * FROM store_status", conn)
    menu_hours_df = pd.read_sql_query("SELECT * FROM menu_hours", conn)
    timezones_df = pd.read_sql_query("SELECT * FROM timezones", conn)

    # Convert timestamps to datetime objects
    store_status_df['timestamp_utc'] = pd.to_datetime(store_status_df['timestamp_utc'])

    # Merge timezone info
    store_status_df = store_status_df.merge(timezones_df, on='store_id', how='left')
    menu_hours_df = menu_hours_df.merge(timezones_df, on='store_id', how='left')

    # Convert business hours to UTC, handling missing timezones and fractional seconds
    menu_hours_df['start_time_utc'] = menu_hours_df.apply(lambda row: safe_convert_to_utc(row, 'timezone_str', 'start_time_local'), axis=1)
    menu_hours_df['end_time_utc'] = menu_hours_df.apply(lambda row: safe_convert_to_utc(row, 'timezone_str', 'end_time_local'), axis=1)

    # Calculate the current UTC time as the max timestamp in store_status
    current_utc = store_status_df['timestamp_utc'].max()

    report_columns = ['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week', 'downtime_last_hour', 'downtime_last_day', 'downtime_last_week']
    report_df = pd.DataFrame(columns=report_columns)

    for store_id in store_status_df['store_id'].unique():
        store_hours = menu_hours_df[menu_hours_df['store_id'] == store_id]
        store_status = store_status_df[store_status_df['store_id'] == store_id]

        report_data = {'store_id': store_id}
        for timeframe, label in zip([1/24, 1, 7], ['hour', 'day', 'week']):
            uptime, downtime = calculate_uptime_downtime(store_status, store_hours, current_utc, timeframe)
            report_data[f'uptime_last_{label}'] = uptime
            report_data[f'downtime_last_{label}'] = downtime

        report_df = pd.concat([report_df, pd.DataFrame([report_data])], ignore_index=True)

    report_path = f'reports/{report_id}.csv'
    report_df.to_csv(report_path, index=False)
    print(f"Report saved to {report_path}")

    conn.close()
